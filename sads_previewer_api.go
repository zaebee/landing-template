package main

import (
	"encoding/json"
	"fmt"
	"html/template"
	"io/fs"
	"io/ioutil"
	"log"
	"net/http"
	"os"
	"path/filepath"
	"strings"

	"github.com/flosch/pongo2/v6"
	"google.golang.org/protobuf/encoding/protojson"
	"google.golang.org/protobuf/proto"
	// Assuming pb "landing-page-generator/generated/go" is accessible
	// If sads_previewer_api.go is in the same package as main.go, it will be.
)

// Base path for SADS components
const sadsComponentsPath = "templates/components"
const sadsDataPath = "data"
const appConfigPath = "public/config.json"

// Helper to load app configuration (simplified, might need adjustment)
func loadAppConfigForPreviewer() (map[string]interface{}, error) {
	data, err := ioutil.ReadFile(appConfigPath)
	if err != nil {
		return nil, fmt.Errorf("failed to read app config %s: %w", appConfigPath, err)
	}
	var config map[string]interface{}
	if err := json.Unmarshal(data, &config); err != nil {
		return nil, fmt.Errorf("failed to unmarshal app config %s: %w", appConfigPath, err)
	}
	return config, nil
}


// API handler to list SADS components
func listSadsComponentsHandler(w http.ResponseWriter, r *http.Request) {
	components := []string{}
	entries, err := ioutil.ReadDir(sadsComponentsPath)
	if err != nil {
		http.Error(w, "Failed to read components directory: "+err.Error(), http.StatusInternalServerError)
		return
	}
	for _, entry := range entries {
		if entry.IsDir() {
			components = append(components, entry.Name())
		}
	}
	w.Header().Set("Content-Type", "application/json")
	json.NewEncoder(w).Encode(components)
}

// API handler to get a SADS component's rendered HTML
// This will require Pongo2 rendering with sample data.
func getSadsComponentHandler(w http.ResponseWriter, r *http.Request) {
	parts := strings.Split(r.URL.Path, "/")
	if len(parts) < 4 {
		http.Error(w, "Invalid component path", http.StatusBadRequest)
		return
	}
	componentName := parts[3]
	componentTemplatePath := filepath.Join(sadsComponentsPath, componentName, componentName+".html")

	if _, err := os.Stat(componentTemplatePath); os.IsNotExist(err) {
		http.Error(w, "Component template not found: "+componentName, http.StatusNotFound)
		return
	}

	// 1. Load App Config to find data mapping
	appConfig, err := loadAppConfigForPreviewer()
	if err != nil {
		log.Printf("Error loading app config for %s: %v", componentName, err)
		// Decide if we proceed without appConfig or error out. For now, proceed.
	}

	// 2. Determine data file and type for this component
	// This logic needs to replicate how main.go's BuildOrchestrator finds data for a block.
	var componentData interface{} // This will hold the actual data (proto.Message or []proto.Message)
	var pongoCompatibleData pongo2.Context // Data in map[string]interface{} format for Pongo

	// Attempt to find block_data_loaders config for this component
	// The componentName here is like "hero", "features".
	// The keys in block_data_loaders are like "templates/components/hero/hero.html".
	componentKeyInConfig := filepath.ToSlash(filepath.Join(sadsComponentsPath, componentName, componentName+".html")) // Ensure forward slashes

	if appConfig != nil {
		if blockLoadersConfig, ok := appConfig["block_data_loaders"].(map[string]interface{}); ok {
			if compLoaderSettings, ok := blockLoadersConfig[componentKeyInConfig].(map[string]interface{}); ok {
				dataFile, _ := compLoaderSettings["data_file"].(string)
				messageTypeName, _ := compLoaderSettings["message_type_name"].(string)
				isList, _ := compLoaderSettings["is_list"].(bool)

				if dataFile != "" && messageTypeName != "" {
					log.Printf("Attempting to load data for component %s: file '%s', type '%s', isList: %t", componentName, dataFile, messageTypeName, isList)

					// Use the existing proto loading logic (simplified)
					// Need access to newMessageInstance and JsonProtoDataLoader from main.go
					// For now, let's assume direct access or we'll refactor them later.
					dataLoader := NewJsonProtoDataLoader() // Assumes NewJsonProtoDataLoader is accessible

					protoInstance, err := newMessageInstance(messageTypeName) // Assumes newMessageInstance is accessible
					if err != nil {
						log.Printf("Error creating new message instance for %s: %v", messageTypeName, err)
					} else {
						if isList {
							loadedData, err := dataLoader.LoadDynamicListData(filepath.Join(sadsDataPath, dataFile), protoInstance)
							if err != nil {
								log.Printf("Error loading list data for %s from %s: %v", componentName, dataFile, err)
							} else {
								componentData = loadedData
							}
						} else {
							loadedData, err := dataLoader.LoadDynamicSingleItemData(filepath.Join(sadsDataPath, dataFile), protoInstance)
							if err != nil {
								log.Printf("Error loading single item data for %s from %s: %v", componentName, dataFile, err)
							} else {
								componentData = loadedData
							}
						}
					}
				} else {
					log.Printf("Data file or message type name not configured for component %s (key: %s)", componentName, componentKeyInConfig)
				}
			} else {
				log.Printf("No loader settings found for component %s (key: %s) in block_data_loaders", componentName, componentKeyInConfig)
			}
		} else {
			log.Printf("block_data_loaders not found or not a map in app config for component %s", componentName)
		}
	} else {
		log.Printf("App config not loaded, cannot determine data for component %s", componentName)
	}

	// Convert proto message(s) to pongo2.Context
	if componentData != nil {
		pongoCompatibleData = make(pongo2.Context)
		switch v := componentData.(type) {
		case []proto.Message:
			var contextItems []pongo2.Context
			for _, item := range v {
				jsonBytes, err := protojson.Marshal(item)
				if err != nil { log.Printf("PongoConvert: Failed to marshal item %T: %v", item, err); continue }
				var itemMap map[string]interface{}
				if err := json.Unmarshal(jsonBytes, &itemMap); err != nil { log.Printf("PongoConvert: Failed to unmarshal item JSON to map: %v", err); continue }
				contextItems = append(contextItems, itemMap)
			}
			pongoCompatibleData["items"] = contextItems
		case proto.Message:
			jsonBytes, err := protojson.Marshal(v)
			if err != nil { log.Printf("PongoConvert: Failed to marshal single item %T: %v", v, err) } else {
				var itemMap map[string]interface{}
				if err := json.Unmarshal(jsonBytes, &itemMap); err != nil { log.Printf("PongoConvert: Failed to unmarshal single item JSON to map: %v", err) } else {
					pongoCompatibleData["item"] = itemMap
				}
			}
		default:
			log.Printf("PongoConvert: Unknown data type %T for component %s", componentData, componentName)
		}
	} else {
		log.Printf("No data loaded for component %s, rendering with empty context or defaults.", componentName)
		pongoCompatibleData = pongo2.Context{} // Ensure it's not nil
	}

	// Add dummy translations for now, actual translation loading might be complex here
	pongoCompatibleData["translations"] = map[string]string{
		"hero_title_placeholder": "Welcome (Preview)",
		"hero_subtitle_placeholder": "This is a preview subtitle.",
		"hero_cta_placeholder": "Learn More (Preview)",
		// Add other keys as needed by components, or load them properly
	}


	// 3. Render the component template with Pongo2
	// Need a Pongo2 template set, similar to main.go
	// The loader should point to the root of templates, so paths like "components/hero/hero.html" work.
	tplSet := pongo2.NewSet("previewer-loader", pongo2.MustNewLocalFileSystemLoader("templates"))
	tpl, err := tplSet.FromFile(filepath.ToSlash(componentTemplatePath)) // Pongo expects forward slashes
	if err != nil {
		http.Error(w, "Failed to load component Pongo2 template "+componentTemplatePath+": "+err.Error(), http.StatusInternalServerError)
		return
	}

	renderedHtml, err := tpl.Execute(pongoCompatibleData)
	if err != nil {
		http.Error(w, "Failed to render component template "+componentName+": "+err.Error(), http.StatusInternalServerError)
		return
	}

	w.Header().Set("Content-Type", "text/html")
	fmt.Fprint(w, renderedHtml)
}


// API handler to get sample data for a SADS component (as JSON)
// This is more for inspection/frontend use if needed, primary rendering uses above handler
func getSadsComponentSampleDataHandler(w http.ResponseWriter, r *http.Request) {
	parts := strings.Split(r.URL.Path, "/")
	if len(parts) < 5 { // /api/sads/component/{name}/sample-data
		http.Error(w, "Invalid component data path", http.StatusBadRequest)
		return
	}
	componentName := parts[3]

	// This logic will be similar to the data loading part of getSadsComponentHandler
	// For brevity in this step, I'll sketch it out.
	// 1. Load App Config
	// 2. Find dataFile, messageTypeName, isList for componentName
	// 3. Load data using JsonProtoDataLoader
	// 4. Marshal loaded proto message(s) to JSON and return

	// Placeholder implementation:
	appConfig, err := loadAppConfigForPreviewer()
	if err != nil {
		http.Error(w, "Failed to load app config: "+err.Error(), http.StatusInternalServerError)
		return
	}

	var componentDataProto interface{}
	componentKeyInConfig := filepath.ToSlash(filepath.Join(sadsComponentsPath, componentName, componentName+".html"))

	if blockLoadersConfig, ok := appConfig["block_data_loaders"].(map[string]interface{}); ok {
		if compLoaderSettings, ok := blockLoadersConfig[componentKeyInConfig].(map[string]interface{}); ok {
			dataFile, _ := compLoaderSettings["data_file"].(string)
			messageTypeName, _ := compLoaderSettings["message_type_name"].(string)
			isList, _ := compLoaderSettings["is_list"].(bool)

			if dataFile != "" && messageTypeName != "" {
				dataLoader := NewJsonProtoDataLoader()
				protoInstance, errInst := newMessageInstance(messageTypeName)
				if errInst != nil {
					log.Printf("SampleData: Error creating instance for %s: %v", messageTypeName, errInst)
				} else {
					if isList {
						componentDataProto, _ = dataLoader.LoadDynamicListData(filepath.Join(sadsDataPath, dataFile), protoInstance)
					} else {
						componentDataProto, _ = dataLoader.LoadDynamicSingleItemData(filepath.Join(sadsDataPath, dataFile), protoInstance)
					}
				}
			}
		}
	}

	if componentDataProto == nil {
		// Return empty JSON object if no data found or error
		w.Header().Set("Content-Type", "application/json")
		fmt.Fprint(w, "{}")
		return
	}

	// Marshal the proto message(s) to JSON
	var jsonResponse []byte
	var marshalErr error

	// protojson.MarshalOptions for consistent output
	mopts := protojson.MarshalOptions{Indent: "  ", EmitUnpopulated: true}

	switch data := componentDataProto.(type) {
	case proto.Message:
		jsonResponse, marshalErr = mopts.Marshal(data)
	case []proto.Message:
		// Need to marshal each item and construct a JSON array
		var itemsJson []json.RawMessage
		for _, item := range data {
			itemJson, err := mopts.Marshal(item)
			if err != nil {
				log.Printf("Error marshalling item for sample data: %v", err)
				continue
			}
			itemsJson = append(itemsJson, itemJson)
		}
		jsonResponse, marshalErr = json.MarshalIndent(itemsJson, "", "  ")
	default:
		marshalErr = fmt.Errorf("unknown data type for JSON marshalling: %T", componentDataProto)
	}

	if marshalErr != nil {
		http.Error(w, "Failed to marshal sample data to JSON: "+marshalErr.Error(), http.StatusInternalServerError)
		return
	}

	w.Header().Set("Content-Type", "application/json")
	w.Write(jsonResponse)
}

// Function to start the previewer API server (can be called from main)
func StartSadsPreviewerServer(port string) {
	mux := http.NewServeMux()
	mux.HandleFunc("/api/sads/components", listSadsComponentsHandler)
	mux.HandleFunc("/api/sads/component/", getSadsComponentHandler) // Path prefix
	mux.HandleFunc("/api/sads/component/", func(w http.ResponseWriter, r *http.Request) { // More specific routing
		if strings.HasSuffix(r.URL.Path, "/sample-data") {
			getSadsComponentSampleDataHandler(w,r)
		} else {
			getSadsComponentHandler(w,r)
		}
	})


	// Serve static files for the previewer tool itself (HTML, JS, CSS for the tool)
	// Assumes previewer's static assets will be in public/sads_previewer_assets/
	// For now, this might not be strictly necessary if sads_previewer.html is also in public/
	// and served by a general static file server.
	// fs := http.FileServer(http.Dir("./public/sads_previewer_assets"))
	// mux.Handle("/sads-previewer-assets/", http.StripPrefix("/sads-previewer-assets/", fs))


	log.Printf("SADS Previewer API server starting on port %s", port)
	if err := http.ListenAndServe(":"+port, mux); err != nil {
		log.Fatalf("Failed to start SADS Previewer API server: %v", err)
	}
}

/*
Note on dependencies from main.go:
- NewJsonProtoDataLoader()
- newMessageInstance()
- protoRegistry (used by newMessageInstance)
- pb "landing-page-generator/generated/go"

These need to be accessible. If sads_previewer_api.go is in the `main` package
and compiled alongside main.go, they should be. Otherwise, refactoring into a shared
package (e.g., `internal/dataproviders` or `internal/protohelpers`) would be needed.
For this phase, I'm assuming they are accessible.
The pongo2 library is also a dependency.
The `go.mod` file should already include pongo2.
*/
