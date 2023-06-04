package main

import (
	"archive/zip"
	"fmt"
	"io"
	"io/ioutil"
	"log"
	"os"
	"path/filepath"
)

func extractFlagRecursive(zipPath string) bool {
	reader, err := zip.OpenReader(zipPath)
	if err != nil {
		log.Fatal(err)
	}

	defer reader.Close()

	for _, file := range reader.File {
		fmt.Println(file.Name)
		if file.Name == "1.zip" {
			extractFile(file)
			os.Exit(0)
		}

		if file.FileInfo().IsDir() {
			continue
		}

		nestedZipReader, err := file.Open()
		if err != nil {
			log.Fatal(err)
		}

		tempDir, err := ioutil.TempDir("", "nested_zip")
		if err != nil {
			log.Fatal(err)
		}

		tempFile, err := ioutil.TempFile(tempDir, "*.zip")
		if err != nil {
			log.Fatal(err)
		}

		_, err = io.Copy(tempFile, nestedZipReader)
		if err != nil {
			log.Fatal(err)
		}

		tempFile.Close()

		if extractFlagRecursive(tempFile.Name()) {
			return true
		}

		err = os.RemoveAll(tempDir)
		if err != nil {
			log.Fatal(err)
		}
	}

	return false
}

func extractFile(file *zip.File) {
	extractedFile, err := file.Open()
	if err != nil {
		log.Fatal(err)
	}

	defer extractedFile.Close()

	outputPath := filepath.Join(".", file.Name)
	outFile, err := os.OpenFile(outputPath, os.O_WRONLY|os.O_CREATE|os.O_TRUNC, file.Mode())
	if err != nil {
		log.Fatal(err)
	}

	defer outFile.Close()

	_, err = io.Copy(outFile, extractedFile)
	if err != nil {
		log.Fatal(err)
	}

	fmt.Printf("Extracted: %s\n", outputPath)
}

func main() {
	flagFound := extractFlagRecursive("65535.zip")
	if flagFound {
		fmt.Println("Flag dosyasi cikarildi!")
	} else {
		fmt.Println("Flag bulunamadi!")
	}
}
