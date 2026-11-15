from pathlib import Path
from typing import List, Any
from langchain_community.document_loaders import PyPDFLoader, TextLoader, CSVLoader
from langchain_community.document_loaders import Docx2txtLoader
# from langchain_community.document_loaders.excel import UnstructuredExcel
from langchain_community.document_loaders import JSONLoader

def load_all_documents(data_dir: str) -> List[Any]:
    """Load all supported files from the data directory and convert to langchain document structure  Supported: PDF, TXT, CSV, Excel, Word, JSON"""

    #use project root data folder
    data_path = Path(data_dir).resolve()
    print(f"[DEBUG] Data path: {data_path}")
    documents = []

    ##PDF files
    pdf_files = list(data_path.glob('**/*.pdf'))
    print(f"[DEBUG] Found {len(pdf_files)} PDF files: {[str(f) for f in pdf_files]}")

    for pdf_file in pdf_files:
        print(f"[DEBUG] Loading PDF: {pdf_file}")
        try:
            loader = PyPDFLoader(str(pdf_file))
            loaded = loader.load()
            print(f"[DEBUG] Loaded {len(loaded)} PDF docs from {pdf_file}")
            documents.extend(loaded)
            
        except Exception as e:
            print(f"[ERROR] failed to load PDF {pdf_file}: {e}")

    return documents

def load_single_document(file_path: str):
    """Load one PDF and return langchain document objects"""

    path = Path(file_path)

    if not path.exists():
        raise FileNotFoundError(f"File not found: {path}")

    if path.suffix.lower() != ".pdf":
        raise ValueError("Only PDF files are supported.")

    loader = PyPDFLoader(str(path))
    documents = loader.load()

    if not documents:
        raise ValueError("No content could be extracted from the PDF.")

    return documents

        


        



