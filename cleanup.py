# cleanup.py
import os
import shutil

# 直接指定项目根目录
BASE_DIR = r"E:\pythonvis1\intelligent_assistant"


def clear_uploads():
    uploads_dir = os.path.join(BASE_DIR, "uploads")
    if os.path.exists(uploads_dir):
        shutil.rmtree(uploads_dir)
        os.makedirs(uploads_dir)
        print("✅ 上传文件已清空")
    else:
        print(f"ℹ️ 目录不存在: {uploads_dir}")


def clear_chromadb():
    chroma_dir = os.path.join(BASE_DIR, "chroma_db")
    if os.path.exists(chroma_dir):
        shutil.rmtree(chroma_dir)
        print("✅ 向量数据库已删除")
    else:
        print(f"ℹ️ 目录不存在: {chroma_dir}")


def clear_database():
    """清空数据库中的文档记录"""
    import subprocess
    try:
        subprocess.run(
            ["docker", "exec", "postgres-dev", "psql", "-U", "postgres", "-d", 
             "intelligent_assistant", "-c", "TRUNCATE documents RESTART IDENTITY;"],
            check=True
        )
        print("✅ 数据库文档记录已清空")
    except Exception as e:
        print(f"❌ 清空数据库失败: {e}")


if __name__ == "__main__":
    print(f"\n📁 项目目录: {BASE_DIR}\n")
    print("1. 清空上传文件 (uploads)")
    print("2. 清空向量数据库 (chroma_db)")
    print("3. 清空数据库记录 (documents)")
    print("4. 清空所有")
    print("0. 退出")
    
    choice = input("\n请选择 (0-4): ").strip()
    
    if choice == "1":
        clear_uploads()
    elif choice == "2":
        clear_chromadb()
    elif choice == "3":
        clear_database()
    elif choice == "4":
        clear_uploads()
        clear_chromadb()
        clear_database()
        print("\n✅ 所有数据已清空！")
    else:
        print("退出")