package main

import (
	"os"

	"github.com/replicate/cog/pkg/cli"
	"github.com/replicate/cog/pkg/util/console"
)

func init() {
	// if catalog-info.yaml exists, copy it to cog.yaml
	if _, ok := os.OpenFile("catalog-info.yaml", os.O_RDONLY, 0); ok == nil {
		// create a file called cog.yaml from catalog-info.yaml
		if err := os.Link("catalog-info.yaml", "cog.yaml"); err != nil {
			// if the file already exists, don't do anything
			if !os.IsExist(err) {
				console.Fatalf("Failed to copy catalog-info.yaml to cog.yaml: %s", err)
			}
		}
	}
}

func main() {
	cmd, err := cli.NewRootCommand()
	if err != nil {
		console.Fatalf("%f", err)
	}

	if err = cmd.Execute(); err != nil {
		console.Fatalf("%s", err)
	}
}
