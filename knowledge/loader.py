"""
文档加载模块

支持从不同来源加载和分割文档
"""
from pathlib import Path
from typing import List, Dict, Any
import uuid


class DocumentLoader:
    """
    文档加载器

    支持从文件或文本加载文档，并自动分割成块
    """

    def __init__(
        self,
        chunk_size: int = 1000,
        chunk_overlap: int = 200,
    ):
        """
        初始化文档加载器

        Args:
            chunk_size: 每个文档块的大小（字符数）
            chunk_overlap: 文档块之间的重叠字符数
        """
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap

    def load_from_text(
        self, text: str, metadata: Dict[str, Any] = None
    ) -> List[Dict[str, Any]]:
        """
        从文本字符串加载文档

        Args:
            text: 文本内容
            metadata: 元数据

        Returns:
            List[Dict]: 文档块列表，每个包含 content、id、metadata
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
        从文件加载文档

        Args:
            file_path: 文件路径
            metadata: 元数据

        Returns:
            List[Dict]: 文档块列表
        """
        path = Path(file_path)

        if not path.exists():
            raise FileNotFoundError(f"文件不存在：{file_path}")

        # 根据文件扩展名选择加载方式
        if path.suffix == ".txt":
            text = self._load_txt(path)
        elif path.suffix == ".pdf":
            text = self._load_pdf(path)
        elif path.suffix == ".md":
            text = self._load_txt(path)
        else:
            text = self._load_txt(path)

        # 添加文件信息到元数据
        if metadata is None:
            metadata = {}
        metadata["source_file"] = str(path)
        metadata["file_type"] = path.suffix

        return self.load_from_text(text, metadata)

    def _split_text(self, text: str) -> List[str]:
        """
        将文本分割成块

        Args:
            text: 要分割的文本

        Returns:
            List[str]: 文本块列表
        """
        if len(text) <= self.chunk_size:
            return [text]

        chunks = []
        start = 0

        while start < len(text):
            end = start + self.chunk_size

            # 尝试在句子边界处分割
            if end < len(text):
                # 查找最近的句子结束符
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
        """加载 TXT 文件"""
        return path.read_text(encoding="utf-8")

    def _load_pdf(self, path: Path) -> str:
        """加载 PDF 文件"""
        try:
            from pypdf import PdfReader

            reader = PdfReader(path)
            text = ""
            for page in reader.pages:
                text += page.extract_text() + "\n\n"
            return text
        except ImportError:
            raise ImportError("请安装 pypdf: pip install pypdf")
