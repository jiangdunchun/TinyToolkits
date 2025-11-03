import qrcode
import os
import zlib
import base64
from PIL import Image
import argparse

class QRFileEncoder:
    def __init__(self, compression_method='zlib'):
        self.compression_method = compression_method
        
    def compress_data(self, data):
        """压缩数据"""
        if self.compression_method == 'zlib':
            return zlib.compress(data, level=zlib.Z_BEST_COMPRESSION)
        elif self.compression_method == 'none':
            return data
        else:
            return zlib.compress(data)  # 默认使用zlib
    
    def decompress_data(self, compressed_data):
        """解压缩数据"""
        if self.compression_method == 'zlib':
            return zlib.decompress(compressed_data)
        elif self.compression_method == 'none':
            return compressed_data
        else:
            return zlib.decompress(compressed_data)
    
    def file_to_qrcodes(self, filename, chunk_size=1000):
        """将文件转换为二维码"""
        # 创建输出目录
        output_dir = f"{filename}_qrcodes"
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
        
        file_size = os.path.getsize(filename)
        total_chunks = (file_size + chunk_size - 1) // chunk_size
        
        with open(filename, "rb") as file:
            for chunk_index in range(total_chunks):
                # 读取数据块
                chunk = file.read(chunk_size)
                if not chunk:
                    break
                
                # 压缩数据
                compressed_chunk = self.compress_data(chunk)
                compression_ratio = len(compressed_chunk) / len(chunk) if len(chunk) > 0 else 1
                
                # 编码为base64
                encoded_data = base64.b64encode(compressed_chunk).decode('utf-8')
                
                # 添加元数据
                metadata = {
                    'index': chunk_index,
                    'total': total_chunks,
                    'original_size': len(chunk),
                    'compressed_size': len(compressed_chunk),
                    'compression': self.compression_method
                }
                
                data_packet = f"{metadata}|{encoded_data}"
                
                # 生成二维码
                qr = qrcode.QRCode(
                    version=None,
                    error_correction=qrcode.constants.ERROR_CORRECT_M,
                    box_size=8,
                    border=2,
                )
                
                qr.add_data(data_packet)
                qr.make(fit=True)
                
                # 保存二维码
                img = qr.make_image(fill_color="black", back_color="white")
                output_path = os.path.join(output_dir, f"{chunk_index:04d}.png")
                img.save(output_path)
                
                print(f"二维码 {chunk_index:04d}: 原始 {len(chunk)}B → 压缩 {len(compressed_chunk)}B "
                      f"(比率: {compression_ratio:.2f})")
        
        print(f"\n完成! 共生成 {total_chunks} 个二维码，保存在 '{output_dir}' 目录中")
        return total_chunks
    
    def qrcodes_to_file(self, qrcode_dir, output_filename):
        """从二维码恢复文件"""
        try:
            from pyzbar.pyzbar import decode as qr_decode
        except ImportError:
            print("请安装pyzbar库: pip install pyzbar")
            return False
        
        qr_files = sorted([f for f in os.listdir(qrcode_dir) if f.endswith('.jpg')])
        
        if not qr_files:
            print(f"在目录 '{qrcode_dir}' 中未找到二维码文件")
            return False
        
        chunks = {}
        successful_decodes = 0
        
        for qr_file in qr_files:
            img_path = os.path.join(qrcode_dir, qr_file)
            try:
                img = Image.open(img_path)
                results = qr_decode(img)
                
                if results:
                    decoded_data = results[0].data.decode('utf-8')
                    
                    # 解析元数据和内容
                    if '|' in decoded_data:
                        metadata_str, encoded_data = decoded_data.split('|', 1)
                        # 安全地解析元数据
                        metadata = {}
                        try:
                            metadata = eval(metadata_str)
                        except:
                            # 如果元数据解析失败，尝试手动解析
                            pass
                        
                        # 解码数据
                        compressed_data = base64.b64decode(encoded_data)
                        original_data = self.decompress_data(compressed_data)
                        
                        # 使用文件名中的索引作为后备
                        try:
                            index_from_filename = int(os.path.splitext(qr_file)[0])
                            chunk_index = metadata.get('index', index_from_filename)
                        except:
                            chunk_index = successful_decodes
                        
                        chunks[chunk_index] = original_data
                        successful_decodes += 1
                        print(f"解码成功: {qr_file} (块 {chunk_index}, 大小: {len(original_data)}B)")
                    else:
                        print(f"数据格式错误: {qr_file}")
                else:
                    print(f"无法解码: {qr_file}")
                
            except Exception as e:
                print(f"处理 {qr_file} 时出错: {e}")
        
        if not chunks:
            print("未成功解码任何二维码")
            return False
        
        # 确保输出目录存在
        output_dir = os.path.dirname(output_filename)
        if output_dir and not os.path.exists(output_dir):
            os.makedirs(output_dir)
        
        # 按顺序组合文件
        with open(output_filename, "wb") as f:
            for i in range(max(chunks.keys()) + 1):
                if i in chunks:
                    f.write(chunks[i])
        
        recovered_size = os.path.getsize(output_filename)
        print(f"\n文件已恢复: {output_filename} (大小: {recovered_size}B)")
        print(f"成功解码: {successful_decodes}/{len(qr_files)} 个二维码")
        return True

def main():
    parser = argparse.ArgumentParser(description="文件到二维码转换器")
    parser.add_argument("filename", help="文件名")
    parser.add_argument("-s", "--size", type=int, default=1000, help="块大小")
    parser.add_argument("-c", "--compress", choices=['zlib', 'none'], default='zlib', 
                       help="压缩方法")
    parser.add_argument("-r", "--recover", action="store_true", help="恢复模式")
    
    args = parser.parse_args()
    
    encoder = QRFileEncoder(args.compress)
    
    if args.recover:
        # 恢复模式：从二维码目录恢复文件，保存为 {filename}_r
        qrcode_dir = f"{args.filename}_qrcodes"
        if not os.path.exists(qrcode_dir):
            print(f"错误: 二维码目录 '{qrcode_dir}' 不存在")
            exit(1)
        
        # 设置恢复文件名为 {args.filename}_r
        output_filename = f"{args.filename}_r"
        success = encoder.qrcodes_to_file(qrcode_dir, output_filename)
        if not success:
            exit(1)
    else:
        # 编码模式：将文件转换为二维码
        if not os.path.exists(args.filename):
            print(f"错误: 文件 '{args.filename}' 不存在")
            exit(1)
        
        file_size = os.path.getsize(args.filename)
        print(f"文件大小: {file_size} 字节")
        
        estimated_qr_count = (file_size + args.size - 1) // args.size
        print(f"预计生成 {estimated_qr_count} 个二维码")
        
        if estimated_qr_count > 100:
            print("警告: 将生成大量二维码，建议使用更大的块大小 (-s 参数)")
            confirm = input("是否继续? (y/N): ")
            if confirm.lower() != 'y':
                print("操作已取消")
                exit(0)
        
        encoder.file_to_qrcodes(args.filename, args.size)

if __name__ == "__main__":
    main()