"""
Document Loader Module

Supports loading and splitting documents from different sources
"""
from pathlib import Path
from typing import List, Dict, Any
import uuid


class DocumentLoader:
    """
    Document loader

    Supports loading documents from files or text, and automatically splitting into chunks
    """

    def __init__(
        self,
        chunk_size: int = 1000,
        chunk_overlap: int = 200,
    ):
        """
        Initialize document loader

        Args:
            chunk_size: Size of each document chunk (characters)
            chunk_overlap: Overlap characters between document chunks
        """
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap

    def load_from_text(
        self, text: str, metadata: Dict[str, Any] = None
    ) -> List[Dict[str, Any]]:
        """
        Load document from text string

        Args:
            text: Text content
            metadata: Metadata

        Returns:
            List[Dict]: List of document chunks, each containing content, id, metadata
        """
        chunks = self._split_text(text)
        documents = []

        for i, chunk in enumerate(chunks):
            doc_metadata = metadata.copy() if metadata else {}
            doc_metadata["chunk_index"] = i
            doc_metadata["total_chunks"] = len(chunks)

            documents.append({
                "id": str(uuid.uuid4()),
                "content": chunk,
                "metadata": doc_metadata,
            })

        return documents

    def load_from_file(
        self, file_path: str, metadata: Dict[str, Any] = None
    ) -> List[Dict[str, Any]]:
        """
        Load document from file

        Args:
            file_path: File path
            metadata: Metadata

        Returns:
            List[Dict]: List of document chunks
        """
        path = Path(file_path)

        if not path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")

        # Choose loading method based on file extension
        if path.suffix == ".txt":
            text = self._load_txt(path)
        elif path.suffix == ".pdf":
            text = self._load_pdf(path)
        elif path.suffix == ".md":
            text = self._load_txt(path)
        else:
            text = self._load_txt(path)

        # Add file information to metadata
        if metadata is None:
            metadata = {}
        metadata["source_file"] = str(path)
        metadata["file_type"] = path.suffix

        return self.load_from_text(text, metadata)

    def _split_text(self, text: str) -> List[str]:
        """
        Split text into chunks

        Args:
            text: Text to split

        Returns:
            List[str]: List of text chunks
        """
        if len(text) <= self.chunk_size:
            return [text]

        chunks = []
        start = 0

        while start < len(text):
            end = start + self.chunk_size

            # Try to split at sentence boundaries
            if end < len(text):
                # Find nearest sentence end
                for sep in ["。", "！", "？", ".", "!", "?", "\n"]:
                    last_sep = text[start:end].rfind(sep)
                    if last_sep != -1:
                        end = start + last_sep + 1
                        break

            chunk = text[start:end].strip()
            if chunk:
                chunks.append(chunk)

            start = end - self.chunk_overlap

        return chunks

    def _load_txt(self, path: Path) -> str:
        """Load TXT file"""
        return path.read_text(encoding="utf-8")

    def _load_pdf(self, path: Path) -> str:
        """Load PDF file"""
        try:
            from pypdf import PdfReader

            reader = PdfReader(path)
            text = ""
            for page in reader.pages:
                text += page.extract_text() + "\n\n"
            return text
        except ImportError:
            raise ImportError("Please install pypdf: pip install pypdf")
