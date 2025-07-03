import subprocess
import logging
from pathlib import Path
from app.config import Config
from app.utils.memory import check_system_resources

logger = logging.getLogger(__name__)

class FFmpegService:
    @staticmethod
    def _run_ffmpeg(cmd: list, timeout: int = Config.TIMEOUT):
        """Execute FFmpeg command with resource checks"""
        check_system_resources()
        try:
            result = subprocess.run(
                cmd,
                check=True,
                timeout=timeout,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )
            logger.debug(f"FFmpeg output: {result.stderr.decode()}")
            return True
        except subprocess.TimeoutExpired:
            logger.error("FFmpeg command timed out")
            raise
        except subprocess.CalledProcessError as e:
            logger.error(f"FFmpeg failed: {e.stderr.decode()}")
            raise

    @staticmethod
    def compress(input_path: Path, output_path: Path, target_resolution="854x480"):
        """Compress video with chunked processing for large files"""
        size_mb = input_path.stat().st_size / (1024 * 1024)
        
        if size_mb > 500:  # Use chunked processing for large files
            return FFmpegService._compress_large_file(input_path, output_path, target_resolution)
        
        cmd = [
            'ffmpeg', '-y',
            '-i', str(input_path),
            '-vf', f'scale={target_resolution}',
            '-c:v', 'libx264',
            '-crf', '23',
            '-preset', 'fast',
            '-c:a', 'aac',
            '-b:a', '128k',
            '-movflags', '+faststart',
            '-max_muxing_queue_size', '9999',
            str(output_path)
        ]
        return FFmpegService._run_ffmpeg(cmd)

    @staticmethod
    def _compress_large_file(input_path: Path, output_path: Path, target_resolution):
        """Process large files in chunks"""
        temp_dir = Path(Config.TEMP_DIR) / f"process_{input_path.stem}"
        temp_dir.mkdir(exist_ok=True)
        
        try:
            # Split into chunks
            FFmpegService._run_ffmpeg([
                'ffmpeg', '-y',
                '-i', str(input_path),
                '-c', 'copy',
                '-f', 'segment',
                '-segment_time', '300',
                '-reset_timestamps', '1',
                str(temp_dir / 'chunk_%03d.mp4')
            ])
            
            # Process each chunk
            processed_chunks = []
            for chunk in sorted(temp_dir.glob('chunk_*.mp4')):
                processed = temp_dir / f"processed_{chunk.name}"
                FFmpegService.compress(chunk, processed, target_resolution)
                processed_chunks.append(processed)
            
            # Concatenate results
            list_file = temp_dir / 'concat_list.txt'
            with open(list_file, 'w') as f:
                for chunk in processed_chunks:
                    f.write(f"file '{chunk}'\n")
            
            FFmpegService._run_ffmpeg([
                'ffmpeg', '-y',
                '-f', 'concat',
                '-safe', '0',
                '-i', str(list_file),
                '-c', 'copy',
                str(output_path)
            ])
            return True
        finally:
            # Cleanup
            for f in temp_dir.glob('*'):
                try:
                    f.unlink()
                except:
                    pass
            try:
                temp_dir.rmdir()
            except:
                pass
