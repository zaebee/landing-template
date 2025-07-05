package main

import (
	"encoding/json"
	"fmt"
	"html/template"
	"io/ioutil"
	"log"
	"os"
	"path/filepath"
	"strings"

	"github.com/flosch/pongo2/v6"
	"google.golang.org/protobuf/encoding/protojson"
	"google.golang.org/protobuf/proto"
	"google.golang.org/protobuf/reflect/protoreflect"
	// "google.golang.org/protobuf/types/known/anypb" // Not used

	// Import the generated protobuf package
	pb "landing-page-generator/generated/go" // Alias for convenience
)

// --- Type Registry for Proto Messages ---

var protoRegistry = make(map[string]protoreflect.MessageType)

func init() {
	protoRegistry["Navigation"] = (&pb.Navigation{}).ProtoReflect().Type()
	protoRegistry["HeroItem"] = (&pb.HeroItem{}).ProtoReflect().Type()
	protoRegistry["FeatureItem"] = (&pb.FeatureItem{}).ProtoReflect().Type()
	protoRegistry["TestimonialItem"] = (&pb.TestimonialItem{}).ProtoReflect().Type()
	protoRegistry["PortfolioItem"] = (&pb.PortfolioItem{}).ProtoReflect().Type()
	protoRegistry["BlogPost"] = (&pb.BlogPost{}).ProtoReflect().Type()
	protoRegistry["ContactFormConfig"] = (&pb.ContactFormConfig{}).ProtoReflect().Type()
}

func newMessageInstance(typeName string) (proto.Message, error) {
	mt, ok := protoRegistry[typeName]
	if !ok {
		return nil, fmt.Errorf("unknown protobuf message type name: %s", typeName)
	}
	return mt.New().Interface(), nil
}

// --- Interfaces ---
type AppConfigManager interface {
	LoadAppConfig() (map[string]interface{}, error)
	GenerateLanguageConfig(baseConfig map[string]interface{}, navData proto.Message, translations map[string]string, lang string) (map[string]interface{}, error)
}
type TranslationProvider interface {
	LoadTranslations(lang string) (map[string]string, error)
}
type DataLoader interface {
	LoadDynamicSingleItemData(filePath string, msg proto.Message) (proto.Message, error)
	LoadDynamicListData(filePath string, baseMsg proto.Message) ([]proto.Message, error)
}
type DataCache interface {
	PreloadData(dataLoadersConfig map[string]interface{}, loader DataLoader) error
	GetItem(key string) (interface{}, bool)
}
type HtmlBlockGenerator interface {
	GenerateHtml(data interface{}, translations map[string]string) (string, error)
}
type PageBuilder interface {
	AssembleTranslatedPage(lang string, translations map[string]string, mainContent string, navigationItems []map[string]interface{}, pageTitle string) (string, error)
}
type AssetBundler interface {
	BundleCss(projectRoot, outputDir string) (string, error)
	BundleJs(projectRoot, outputDir string) (string, error)
}

// --- Implementations ---
type DefaultAppConfigManager struct{}

func (m *DefaultAppConfigManager) LoadAppConfig() (map[string]interface{}, error) {
	configPath := "public/config.json"
	log.Printf("Loading app config from: %s", configPath)
	data, err := ioutil.ReadFile(configPath)
	if err != nil { return nil, fmt.Errorf("failed to read app config %s: %w", configPath, err) }
	var config map[string]interface{}
	if err := json.Unmarshal(data, &config); err != nil { return nil, fmt.Errorf("failed to unmarshal app config %s: %w", configPath, err) }
	log.Println("App config loaded successfully.")
	return config, nil
}

func (m *DefaultAppConfigManager) GenerateLanguageConfig(baseConfig map[string]interface{}, navData proto.Message, translations map[string]string, lang string) (map[string]interface{}, error) {
	log.Printf("Generating language config for: %s", lang)
	langConfig := make(map[string]interface{})
	for k, v := range baseConfig { langConfig[k] = v }
	if navData != nil {
		navJson, err := protojson.Marshal(navData)
		if err != nil { return nil, fmt.Errorf("failed to marshal navData for lang %s: %w", lang, err) }
		var navMap map[string]interface{}
		if err := json.Unmarshal(navJson, &navMap); err != nil { return nil, fmt.Errorf("failed to unmarshal navJson to map for lang %s: %w", lang, err) }
		langConfig["navigation"] = navMap
	}
	langConfig["translations"] = translations
	langConfig["current_language"] = lang
	if siteNameKey, ok := baseConfig["site_name_key"].(string); ok {
		if translatedSiteName, tOk := translations[siteNameKey]; tOk {
			langConfig["site_name"] = translatedSiteName
		} else {
			langConfig["site_name"] = "Default Site Name"
		}
	}
	log.Printf("Language config generated for %s", lang)
	return langConfig, nil
}

type DefaultTranslationProvider struct{}

func (tp *DefaultTranslationProvider) LoadTranslations(lang string) (map[string]string, error) {
	filePath := filepath.Join("public", "locales", lang+".json")
	log.Printf("Loading translations for lang '%s' from %s", lang, filePath)
	data, err := ioutil.ReadFile(filePath)
	if err != nil { return nil, fmt.Errorf("failed to read translations file %s: %w", filePath, err) }
	var translations map[string]string
	if err := json.Unmarshal(data, &translations); err != nil { return nil, fmt.Errorf("failed to unmarshal translations %s: %w", filePath, err) }
	log.Printf("Translations loaded for lang '%s'", lang)
	return translations, nil
}

type BuildOrchestrator struct {
	appConfigManager AppConfigManager
	translationProvider TranslationProvider
	dataLoader DataLoader
	dataCache DataCache
	pageBuilder PageBuilder
	htmlGenerators map[string]HtmlBlockGenerator
	assetBundler AssetBundler
	appConfig map[string]interface{}
	navProtoData *pb.Navigation
}

func NewBuildOrchestrator(appConfigManager AppConfigManager, translationProvider TranslationProvider, dataLoader DataLoader, dataCache DataCache, pageBuilder PageBuilder, htmlGenerators map[string]HtmlBlockGenerator, assetBundler AssetBundler) *BuildOrchestrator {
	return &BuildOrchestrator{
		appConfigManager: appConfigManager,
		translationProvider: translationProvider,
		dataLoader: dataLoader,
		dataCache: dataCache,
		pageBuilder: pageBuilder,
		htmlGenerators: htmlGenerators,
		assetBundler: assetBundler,
	}
}

func (o *BuildOrchestrator) LoadInitialConfigurations() error {
	log.Println("Loading initial configurations...")
	var err error
	o.appConfig, err = o.appConfigManager.LoadAppConfig()
	if err != nil { return fmt.Errorf("failed to load app config: %w", err) }
	navDataFile, ok := o.appConfig["navigation_data_file"].(string)
	if !ok {
		log.Println("Warning: 'navigation_data_file' not found or not a string in app config. Using default 'data/navigation.json'.")
		navDataFile = "data/navigation.json"
	}
	navMessage := &pb.Navigation{}
	loadedNavData, err := o.dataLoader.LoadDynamicSingleItemData(navDataFile, navMessage)
	if err != nil {
		log.Printf("Warning: failed to load navigation data from %s: %v. Proceeding without navigation data.", navDataFile, err)
		o.navProtoData = nil
	} else {
		concreteNavData, ok := loadedNavData.(*pb.Navigation)
		if !ok {
			log.Printf("Warning: loaded navigation data from %s is not of expected type *pb.Navigation. Type was %T", navDataFile, loadedNavData)
			o.navProtoData = nil
		} else {
			o.navProtoData = concreteNavData
			log.Println("Navigation data loaded successfully.")
		}
	}
	log.Println("Initial configurations loaded.")
	return nil
}

func (o *BuildOrchestrator) generateLanguageSpecificConfig(lang string, translations map[string]string) error {
	log.Printf("Generating language specific config for '%s'", lang)
	langSpecificConfig, err := o.appConfigManager.GenerateLanguageConfig(o.appConfig, o.navProtoData, translations, lang)
	if err != nil { return fmt.Errorf("failed to generate language config for %s: %w", lang, err) }
	generatedConfigDir := filepath.Join("public", "generated_configs")
	if err := os.MkdirAll(generatedConfigDir, 0755); err != nil { return fmt.Errorf("failed to create directory %s: %w", generatedConfigDir, err) }
	generatedConfigPath := filepath.Join(generatedConfigDir, fmt.Sprintf("config_%s.json", lang))
	jsonData, err := json.MarshalIndent(langSpecificConfig, "", "    ")
	if err != nil { return fmt.Errorf("failed to marshal language-specific config for %s: %w", lang, err) }
	if err := ioutil.WriteFile(generatedConfigPath, jsonData, 0644); err != nil { return fmt.Errorf("failed to write language-specific config to %s: %w", generatedConfigPath, err) }
	log.Printf("Successfully wrote language-specific config to %s", generatedConfigPath)
	return nil
}

func (o *BuildOrchestrator) BuildAllLanguages() error {
	log.Println("Starting build for all languages...")
	if err := o.LoadInitialConfigurations(); err != nil { return fmt.Errorf("error loading initial configurations: %w", err) }
	// projectRoot, err := getProjectRoot() // No longer used directly in this function after bundler calls removed
	// if err != nil { return fmt.Errorf("failed to get project root: %w", err) }
	// assetOutputDir := filepath.Join(projectRoot, "public", "dist") // No longer creating dist for these assets
	// if err := os.MkdirAll(assetOutputDir, 0755); err != nil { return fmt.Errorf("failed to create asset output directory %s: %w", assetOutputDir, err) }

	// cssBundlePath, err := o.assetBundler.BundleCss(projectRoot, assetOutputDir)
	// if err != nil { log.Printf("Warning: CSS bundling failed: %v", err) } else if cssBundlePath == "" { log.Println("Warning: CSS bundling produced no output.") } else { log.Printf("CSS bundled to: %s", cssBundlePath) }
	// jsBundlePath, err := o.assetBundler.BundleJs(projectRoot, assetOutputDir)
	// if err != nil { log.Printf("Warning: JS bundling failed: %v", err) } else if jsBundlePath == "" { log.Println("Warning: JavaScript bundling produced no output.") } else { log.Printf("JS bundled to: %s", jsBundlePath) }

	supportedLangsRaw, ok := o.appConfig["supported_langs"].([]interface{})
	if !ok {
		log.Println("Warning: 'supported_langs' not found or not an array in app config. Using defaults ['en', 'es'].")
		supportedLangsRaw = []interface{}{"en", "es"}
	}
	var supportedLangs []string
	for _, langRaw := range supportedLangsRaw {
		if langStr, ok := langRaw.(string); ok { supportedLangs = append(supportedLangs, langStr) } else { log.Printf("Warning: non-string language code found in 'supported_langs': %v", langRaw) }
	}
	defaultLang, _ := o.appConfig["default_lang"].(string)
	if defaultLang == "" {
		log.Println("Warning: 'default_lang' not found or not a string in app config. Using default 'en'.")
		defaultLang = "en"
	}
	blockLoadersConfigRaw, _ := o.appConfig["block_data_loaders"].(map[string]interface{})
	if err := o.dataCache.PreloadData(blockLoadersConfigRaw, o.dataLoader); err != nil { return fmt.Errorf("error preloading data: %w", err) }
	var processedNavItems []map[string]interface{}
	if o.navProtoData != nil {
		for _, item := range o.navProtoData.Items {
			processedNavItems = append(processedNavItems, map[string]interface{}{"label": map[string]string{"key": item.Label.Key}, "href": item.Href, "animation_hint": item.AnimationHint})
		}
		log.Printf("Processed %d navigation items.", len(processedNavItems))
	}
	for _, lang := range supportedLangs {
		log.Printf("Processing language: %s", lang)
		translations, err := o.translationProvider.LoadTranslations(lang)
		if err != nil { log.Printf("Warning: Failed to load translations for lang %s: %v. Skipping this language.", lang, err); continue }
		if err := o.generateLanguageSpecificConfig(lang, translations); err != nil { log.Printf("Warning: Failed to generate language specific config for %s: %v", lang, err) }
		assembledMainContent, err := o.assembleMainContentForLang(lang, translations, blockLoadersConfigRaw)
		if err != nil { log.Printf("Warning: Failed to assemble main content for lang %s: %v. Skipping page generation.", lang, err); continue }
		pageTitleUntranslated, ok := translations["page_title_default"]
		if !ok { pageTitleUntranslated = "Simple Landing Page" }
		pageTitle := translations[fmt.Sprintf("page_title_landing_%s", lang)]
		if pageTitle == "" { pageTitle = pageTitleUntranslated }
		fullHtmlContent, err := o.pageBuilder.AssembleTranslatedPage(lang, translations, assembledMainContent, processedNavItems, pageTitle)
		if err != nil { log.Printf("Warning: Failed to assemble translated page for lang %s: %v. Skipping page generation.", lang, err); continue }
		outputFilename := fmt.Sprintf("index_%s.html", lang)
		if lang == defaultLang { outputFilename = "index.html" }
		if err := o.writeOutputFile(outputFilename, fullHtmlContent); err != nil { log.Printf("Warning: Failed to write output file %s: %v", outputFilename, err) }
	}
	log.Println("Build process complete.")
	return nil
}

func (o *BuildOrchestrator) assembleMainContentForLang(lang string, translations map[string]string, blockLoadersConfig map[string]interface{}) (string, error) {
	log.Printf("Assembling main content for lang: %s", lang)
	var blocksHtmlParts []string
	blockFilenamesRaw, ok := o.appConfig["blocks"].([]interface{})
	if !ok { return "", fmt.Errorf("'blocks' configuration is missing or not an array") }
	for _, blockFilenameRaw := range blockFilenamesRaw {
		blockFilename, ok := blockFilenameRaw.(string)
		if !ok { log.Printf("Warning: Invalid block file entry in config: %v. Skipping.", blockFilenameRaw); continue }
		log.Printf("Processing block: %s for lang %s", blockFilename, lang)
		htmlGenerator, generatorExists := o.htmlGenerators[blockFilename]
		blockConfigRaw, blockConfigExists := blockLoadersConfig[blockFilename]
		var generatedHtmlForBlock string
		var err error
		if generatorExists && blockConfigExists {
			blockConfig, bcOk := blockConfigRaw.(map[string]interface{})
			if !bcOk {
				log.Printf("Warning: Invalid block loader config for '%s'. Skipping data injection.", blockFilename)
				generatedHtmlForBlock, err = htmlGenerator.GenerateHtml(nil, translations)
				if err != nil { log.Printf("Error generating HTML for block %s (static attempt): %v. Skipping.", blockFilename, err); continue }
			} else {
				dataFile, _ := blockConfig["data_file"].(string)
				isList, _ := blockConfig["is_list"].(bool)
				var dataItems interface{}
				var foundInCache bool
				if dataFile != "" {
					dataItems, foundInCache = o.dataCache.GetItem(dataFile)
					if !foundInCache { log.Printf("Warning: Data for file '%s' (block '%s') not found in cache. Block may be static or data loading failed.", dataFile, blockFilename) }
				}
				if isList && (!foundInCache || dataItems == nil) { dataItems = []proto.Message{} } else if !isList && !foundInCache { dataItems = nil }
				generatedHtmlForBlock, err = htmlGenerator.GenerateHtml(dataItems, translations)
				if err != nil { log.Printf("Error generating HTML for block %s with data %s: %v. Skipping.", blockFilename, dataFile, err); continue }
			}
		} else if generatorExists {
			log.Printf("Info: No specific data loader config for block '%s'. Assuming it might be static or take global data.", blockFilename)
			generatedHtmlForBlock, err = htmlGenerator.GenerateHtml(nil, translations)
			if err != nil { log.Printf("Error generating HTML for block %s (no data config): %v. Skipping.", blockFilename, err); continue }
		} else {
			log.Printf("Warning: No HTML generator found for block: %s. This block will be skipped.", blockFilename)
			continue
		}
		blocksHtmlParts = append(blocksHtmlParts, generatedHtmlForBlock)
	}
	return strings.Join(blocksHtmlParts, "\n"), nil
}

func (o *BuildOrchestrator) writeOutputFile(filename string, content string) error {
	log.Printf("Writing %s", filename)
	if err := ioutil.WriteFile(filename, []byte(content), 0644); err != nil { return fmt.Errorf("failed to write file %s: %w", filename, err) }
	return nil
}

type DefaultPageBuilder struct {
	translationProvider TranslationProvider
	pongoSet            *pongo2.TemplateSet
}

func NewDefaultPageBuilder(tp TranslationProvider) *DefaultPageBuilder {
	return &DefaultPageBuilder{
		translationProvider: tp,
		pongoSet:            pongo2.NewSet("file-loader", pongo2.MustNewLocalFileSystemLoader("templates")),
	}
}

func (pb *DefaultPageBuilder) AssembleTranslatedPage(lang string, translations map[string]string, mainContent string, navigationItems []map[string]interface{}, pageTitle string) (string, error) {
	log.Printf("Assembling translated page for lang: %s", lang)
	baseTpl, err := pb.pongoSet.FromFile("base.html")
	if err != nil { return "", fmt.Errorf("failed to load base template: %w", err) }
	context := pongo2.Context{
		"lang": lang,
		"translations": translations,
		"main_content": template.HTML(mainContent),
		"navigation_items": navigationItems,
		"page_title": pageTitle,
	}
	context["sads_style_engine_path"] = "js/sads-style-engine.js"
	context["sads_default_theme_path"] = "js/sads-default-theme.js"
	context["app_js_path"] = "js/app.js"
	context["style_css_path"] = "style.css"
	context["config_json_path"] = fmt.Sprintf("generated_configs/config_%s.json", lang)
	htmlResult, err := baseTpl.Execute(context)
	if err != nil { return "", fmt.Errorf("failed to execute base template for lang %s: %w", lang, err) }
	log.Printf("Successfully assembled page for lang %s", lang)
	return htmlResult, nil
}

func main() {
	log.Println("Build script started...")
	appConfigMgr := &DefaultAppConfigManager{}
	translationProvider := &DefaultTranslationProvider{}
	dataLoader := NewJsonProtoDataLoader()
	dataCache := NewInMemoryDataCache()
	pageBuilder := NewDefaultPageBuilder(translationProvider)
	assetBundler := &DefaultAssetBundler{}
	pongoSet := pongo2.NewSet("file-loader", pongo2.MustNewLocalFileSystemLoader("templates"))
	htmlGenerators := make(map[string]HtmlBlockGenerator)
	if appCfg, err := appConfigMgr.LoadAppConfig(); err == nil {
		if blockFiles, ok := appCfg["blocks"].([]interface{}); ok {
			for _, bfRaw := range blockFiles {
				if blockFilename, ok := bfRaw.(string); ok {
					// Corrected: Use blockFilename directly as it's already the relative path
					htmlGenerators[blockFilename] = NewGenericBlockGenerator(pongoSet, blockFilename)
					log.Printf("Registered GenericBlockGenerator for: %s", blockFilename)
				}
			}
		}
	} else {
		log.Printf("Warning: Could not load app config to register block generators: %v", err)
	}
	orchestrator := NewBuildOrchestrator(appConfigMgr, translationProvider, dataLoader, dataCache, pageBuilder, htmlGenerators, assetBundler)
	if err := orchestrator.BuildAllLanguages(); err != nil { log.Fatalf("Build process failed: %v", err) }
	log.Println("Build script finished successfully.")
}

type JsonProtoDataLoader struct {}

func NewJsonProtoDataLoader() *JsonProtoDataLoader { return &JsonProtoDataLoader{} }

func (l *JsonProtoDataLoader) LoadDynamicSingleItemData(filePath string, msg proto.Message) (proto.Message, error) {
	log.Printf("Attempting to load single item from: %s into type %T", filePath, msg)
	jsonData, err := ioutil.ReadFile(filePath)
	if err != nil { return nil, fmt.Errorf("failed to read data file %s: %w", filePath, err) }
	// Corrected: Instantiate UnmarshalOptions then call Unmarshal method
	unmarshalOpts := protojson.UnmarshalOptions{DiscardUnknown: true}
	if err := unmarshalOpts.Unmarshal(jsonData, msg); err != nil {
		return nil, fmt.Errorf("failed to unmarshal JSON from %s into %T: %w", filePath, msg, err)
	}
	log.Printf("Successfully loaded and unmarshalled single item from %s", filePath)
	return msg, nil
}

func (l *JsonProtoDataLoader) LoadDynamicListData(filePath string, itemExampleInstance proto.Message) ([]proto.Message, error) {
	log.Printf("Attempting to load list data from: %s, base item type %T", filePath, itemExampleInstance)
	jsonData, err := ioutil.ReadFile(filePath)
	if err != nil { return nil, fmt.Errorf("failed to read data file %s: %w", filePath, err) }
	var rawItems []json.RawMessage
	if err := json.Unmarshal(jsonData, &rawItems); err != nil { return nil, fmt.Errorf("failed to unmarshal JSON array from %s: %w", filePath, err) }
	var messages []proto.Message
	itemType := itemExampleInstance.ProtoReflect().Type()
	// Corrected: Instantiate UnmarshalOptions then call Unmarshal method
	unmarshalOpts := protojson.UnmarshalOptions{DiscardUnknown: true}
	for i, rawItem := range rawItems {
		newItem := itemType.New().Interface()
		if err := unmarshalOpts.Unmarshal(rawItem, newItem); err != nil {
			log.Printf("Warning: failed to unmarshal item %d from %s into %T: %v. Skipping item.", i, filePath, newItem, err)
			continue
		}
		messages = append(messages, newItem)
	}
	log.Printf("Successfully loaded and unmarshalled %d items from %s", len(messages), filePath)
	return messages, nil
}

type InMemoryDataCache struct { cache map[string]interface{} }

func NewInMemoryDataCache() *InMemoryDataCache { return &InMemoryDataCache{cache: make(map[string]interface{})} }

func (c *InMemoryDataCache) PreloadData(dataLoadersConfig map[string]interface{}, loader DataLoader) error {
	log.Println("Preloading data into cache...")
	if dataLoadersConfig == nil { log.Println("No dataLoadersConfig provided, skipping preload."); return nil }
	for blockName, configRaw := range dataLoadersConfig {
		config, ok := configRaw.(map[string]interface{})
		if !ok { log.Printf("Warning: Invalid config format for block '%s' in dataLoadersConfig. Skipping.", blockName); continue }
		dataFile, dfOk := config["data_file"].(string)
		messageTypeName, mtnOk := config["message_type_name"].(string)
		if !dfOk || !mtnOk { log.Printf("Warning: 'data_file' or 'message_type_name' missing for block '%s'. Skipping preload for this entry.", blockName); continue }
		if _, exists := c.cache[dataFile]; exists { log.Printf("Data for file '%s' already in cache. Skipping preload.", dataFile); continue }
		isList, _ := config["is_list"].(bool)
		itemInstance, err := newMessageInstance(messageTypeName)
		if err != nil { log.Printf("Warning: Failed to create instance for message type '%s' (block '%s', file '%s'): %v. Skipping.", messageTypeName, blockName, dataFile, err); continue }
		log.Printf("Preloading data for block '%s': file '%s', type '%s', isList: %t", blockName, dataFile, messageTypeName, isList)
		if isList {
			items, err := loader.LoadDynamicListData(dataFile, itemInstance)
			if err != nil { log.Printf("Warning: Error loading list data for file '%s' (block '%s'): %v. Data not cached.", dataFile, blockName, err); continue }
			c.cache[dataFile] = items
			log.Printf("Cached %d items for %s", len(items), dataFile)
		} else {
			item, err := loader.LoadDynamicSingleItemData(dataFile, itemInstance)
			if err != nil { log.Printf("Warning: Error loading single item data for file '%s' (block '%s'): %v. Data not cached.", dataFile, blockName, err); continue }
			c.cache[dataFile] = item
			log.Printf("Cached single item for %s", dataFile)
		}
	}
	log.Println("Data preloading complete.")
	return nil
}

func (c *InMemoryDataCache) GetItem(key string) (interface{}, bool) { item, found := c.cache[key]; return item, found }

type DefaultAssetBundler struct{}

func (ab *DefaultAssetBundler) BundleCss(projectRoot, outputDir string) (string, error) {
	log.Println("AssetBundler: BundleCss called - No longer copying style.css to dist.")
	// sourceCss := filepath.Join(projectRoot, "public", "style.css")
	// destDir := filepath.Join(outputDir)
	// if err := os.MkdirAll(destDir, 0755); err != nil { return "", fmt.Errorf("failed to create destination directory %s for CSS: %w", destDir, err) }
	// destCss := filepath.Join(destDir, "style.css")
	// if _, err := os.Stat(sourceCss); os.IsNotExist(err) { log.Printf("Source CSS %s does not exist. Skipping bundling.", sourceCss); return "", nil }
	// input, err := ioutil.ReadFile(sourceCss)
	// if err != nil { return "", fmt.Errorf("failed to read source CSS %s: %w", sourceCss, err) }
	// if err = ioutil.WriteFile(destCss, input, 0644); err != nil { return "", fmt.Errorf("failed to write destination CSS %s: %w", destCss, err) }
	// log.Printf("CSS 'bundled' to %s", destCss)
	// return destCss, nil
	return "", nil // Returning empty path as it's no longer processed here.
}

func (ab *DefaultAssetBundler) BundleJs(projectRoot, outputDir string) (string, error) {
	log.Println("AssetBundler: BundleJs called - No longer copying JS files to dist, tsc handles output to public/js.")
	// jsFiles := []string{"app.js", "sads-default-theme.js", "sads-style-engine.js"}
	// var createdFiles []string
	// destJsDir := filepath.Join(outputDir, "js") // e.g. public/dist/js
	// if err := os.MkdirAll(destJsDir, 0755); err != nil { return "", fmt.Errorf("failed to create destination directory %s for JS: %w", destJsDir, err) }
	// for _, jsFile := range jsFiles {
	// 	sourceJs := filepath.Join(projectRoot, "public", "js", jsFile) // Source from public/js (where tsc compiles)
	// 	destJs := filepath.Join(destJsDir, jsFile)
	// 	if _, err := os.Stat(sourceJs); os.IsNotExist(err) { log.Printf("Source JS %s does not exist. Skipping.", sourceJs); continue }
	// 	input, err := ioutil.ReadFile(sourceJs)
	// 	if err != nil { log.Printf("Failed to read source JS %s: %v. Skipping.", sourceJs, err); continue }
	// 	if err = ioutil.WriteFile(destJs, input, 0644); err != nil { log.Printf("Failed to write destination JS %s: %v. Skipping.", destJs, err); continue }
	// 	log.Printf("JS file 'copied' to %s", destJs)
	// 	createdFiles = append(createdFiles, destJs)
	// }
	// if len(createdFiles) > 0 { return filepath.Join(filepath.Base(outputDir), "js"), nil }
	return "", nil // Returning empty path as it's no longer processed here.
}

func getProjectRoot() (string, error) { return os.Getwd() }

type GenericBlockGenerator struct {
	pongoSet     *pongo2.TemplateSet
	templatePath string
}

// Corrected: NewGenericBlockGenerator now uses blockFilename directly.
func NewGenericBlockGenerator(pongoSet *pongo2.TemplateSet, blockFilename string) *GenericBlockGenerator {
	return &GenericBlockGenerator{
		pongoSet:     pongoSet,
		templatePath: blockFilename,
	}
}

func (g *GenericBlockGenerator) GenerateHtml(data interface{}, translations map[string]string) (string, error) {
	log.Printf("GenericBlockGenerator: Generating HTML for template %s", g.templatePath)
	tpl, err := g.pongoSet.FromFile(g.templatePath)
	if err != nil { return "", fmt.Errorf("failed to load template %s: %w", g.templatePath, err) }
	var itemsData interface{}
	var itemData interface{}
	if data != nil {
		switch v := data.(type) {
		case []proto.Message:
			var contextItems []pongo2.Context
			for _, item := range v {
				jsonBytes, err := protojson.Marshal(item)
				if err != nil { log.Printf("Warning: Failed to marshal item %T to JSON for template %s: %v", item, g.templatePath, err); continue }
				var itemMap map[string]interface{}
				if err := json.Unmarshal(jsonBytes, &itemMap); err != nil { log.Printf("Warning: Failed to unmarshal item JSON to map for template %s: %v", g.templatePath, err); continue }
				contextItems = append(contextItems, itemMap)
			}
			itemsData = contextItems
		case proto.Message:
			jsonBytes, err := protojson.Marshal(v)
			if err != nil { log.Printf("Warning: Failed to marshal single item %T to JSON for template %s: %v", v, g.templatePath, err) } else {
				var itemMap map[string]interface{}
				if err := json.Unmarshal(jsonBytes, &itemMap); err != nil { log.Printf("Warning: Failed to unmarshal single item JSON to map for template %s: %v", g.templatePath, err) } else {
					itemData = itemMap
				}
			}
		default:
			log.Printf("Warning: Unknown data type %T passed to GenericBlockGenerator for %s", data, g.templatePath)
		}
	}
	context := pongo2.Context{
		"translations": translations,
		"items":        itemsData,
		"item":         itemData,
	}
	htmlResult, err := tpl.Execute(context)
	if err != nil { return "", fmt.Errorf("failed to execute template %s: %w", g.templatePath, err) }
	return htmlResult, nil
}
