import sqlite3
import hashlib
from typing import Optional, Tuple, List

class PDFCache:
    def __init__(self, db_path: str = 'pdf_cache.db'):
        """初始化PDF缓存数据库"""
        self.db_path = db_path
        self._init_db()
    
    def _init_db(self):
        """初始化数据库表结构"""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS pdf_cache (
                    md5_hash TEXT PRIMARY KEY,
                    content TEXT NOT NULL,
                    chapter_data TEXT NOT NULL,
                    character_data TEXT NOT NULL,
                    translation TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            conn.commit()
    
    def calculate_md5(self, file_path: str) -> str:
        """计算文件的MD5哈希值"""
        try:
            hash_md5 = hashlib.md5()
            print(f"开始计算文件MD5：{file_path}")
            with open(file_path, 'rb') as f:
                for chunk in iter(lambda: f.read(4096), b""):
                    hash_md5.update(chunk)
            md5_value = hash_md5.hexdigest()
            print(f"文件MD5计算完成：{md5_value}")
            return md5_value
        except Exception as e:
            print(f"计算MD5哈希值失败：{str(e)}")
            raise e

    def get_cache(self, file_path: str) -> Optional[Tuple[str, List[List[str]], List[List[str]]]]:
        """获取缓存的处理结果"""
        print(f"尝试获取缓存，文件路径：{file_path}")
        try:
            md5_hash = self.calculate_md5(file_path)
            if not md5_hash:
                print("MD5计算失败，无法获取缓存")
                return None

            print(f"查询数据库，MD5：{md5_hash}")
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.execute(
                    "SELECT content, chapter_data, character_data, translation FROM pdf_cache WHERE md5_hash = ?",
                    (md5_hash,)
                )
                result = cursor.fetchone()
                if result:
                    print(f"找到缓存记录：{md5_hash}")
                    import json
                    content = result[0]
                    chapter_data = json.loads(result[1])
                    character_data = json.loads(result[2])
                    translation = result[3]
                    return content, chapter_data, character_data, translation
                else:
                    print(f"未找到缓存记录：{md5_hash}")
                return None
        except Exception as e:
            print(f"获取缓存失败：{str(e)}")
            return None
    
    def save_cache(self, file_path: str, content: str, chapter_data: List[List[str]], character_data: List[List[str]], translation: str = None) -> bool:
        """保存处理结果到缓存"""
        try:
            print(f"开始保存缓存，文件路径：{file_path}")
            md5_hash = self.calculate_md5(file_path)
            #print(f"准备写入数据库，MD5：{md5_hash, content,chapter_data,character_data}")
            with sqlite3.connect(self.db_path) as conn:
                import json
                conn.execute(
                    "INSERT OR REPLACE INTO pdf_cache (md5_hash, content, chapter_data, character_data, translation) VALUES (?, ?, ?, ?, ?)",
                    (md5_hash, content, json.dumps(chapter_data), json.dumps(character_data), translation)
                )
                conn.commit()
            print(f"缓存保存成功：{md5_hash}")
            return True
        except Exception as e:
            print(f"保存缓存失败：{str(e)}")
            return False