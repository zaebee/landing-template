package htmlgen

import (
	"html/template"
	"io"
	// "os" // Not needed directly in this file for generating to io.Writer
)

const defaultHTMLTemplate = `<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Task Flow Visualization</title>
    <style>
        body { font-family: sans-serif; margin: 20px; }
        .mermaid { text-align: center; } /* Basic styling for the mermaid div */
    </style>
</head>
<body>
    <h1>Task Flow Diagram</h1>
    <div class="mermaid">
{{.MermaidMarkdown}}
    </div>
    <script src="https://cdn.jsdelivr.net/npm/mermaid/dist/mermaid.min.js"></script>
    <script>
        mermaid.initialize({ startOnLoad: true });
    </script>
</body>
</html>
`

// HTMLPageData holds the data needed to render the HTML page.
type HTMLPageData struct {
	MermaidMarkdown string
	FlowName        string // Optional: could be used in title or header
}

// GenerateHTMLPage generates a simple HTML page that renders the given Mermaid markdown.
// It writes the output to the provided io.Writer.
func GenerateHTMLPage(writer io.Writer, data HTMLPageData) error {
	tmpl, err := template.New("htmlPage").Parse(defaultHTMLTemplate)
	if err != nil {
		return err
	}

	err = tmpl.Execute(writer, data)
	if err != nil {
		return err
	}

	return nil
}
