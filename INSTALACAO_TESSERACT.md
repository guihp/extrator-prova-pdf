# 📦 Instalação do Tesseract OCR

O sistema agora usa OCR para extrair texto de imagens do PDF. É necessário instalar o Tesseract.

## macOS

```bash
brew install tesseract
brew install tesseract-lang  # Para suporte a português
```

## Linux (Ubuntu/Debian)

```bash
sudo apt-get update
sudo apt-get install tesseract-ocr
sudo apt-get install tesseract-ocr-por  # Para português
```

## Linux (Fedora)

```bash
sudo dnf install tesseract
sudo dnf install tesseract-langpack-por
```

## Windows

1. Baixe o instalador: https://github.com/UB-Mannheim/tesseract/wiki
2. Instale o Tesseract
3. Adicione ao PATH ou configure no código:
   ```python
   pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
   ```

## Verificar Instalação

```bash
tesseract --version
tesseract --list-langs  # Deve incluir 'por' para português
```

## Nota

Se o Tesseract não estiver instalado, o sistema continuará funcionando, mas sem OCR.
As questões serão extraídas apenas do texto selecionável do PDF.




