import os
import sys
import subprocess
import paramiko
import logging
from pathlib import Path

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def connect_to_oracle(key_path, oracle_ip, username='ubuntu'):
    """Connect to Oracle Cloud instance"""
    try:
        logger.info(f"Connecting to Oracle instance at {oracle_ip}")
        key = paramiko.RSAKey.from_private_key_file(key_path)
        client = paramiko.SSHClient()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        client.connect(oracle_ip, username=username, pkey=key)
        logger.info("Successfully connected to Oracle")
        return client
    except Exception as e:
        logger.error(f"Failed to connect to Oracle: {str(e)}")
        sys.exit(1)

def check_disk_space(ssh_client, min_space_gb=5):
    """Check if there's enough disk space available"""
    try:
        # Check space on /mnt/data instead of /
        stdin, stdout, stderr = ssh_client.exec_command("df -h /mnt/data | tail -1 | awk '{print $4}'")
        available_space = stdout.read().decode().strip()
        
        # Convert to GB if in different format
        if 'G' in available_space:
            space_gb = float(available_space.replace('G', ''))
        elif 'M' in available_space:
            space_gb = float(available_space.replace('M', '')) / 1024
        else:
            space_gb = 0
            
        if space_gb < min_space_gb:
            logger.error(f"Low disk space: {space_gb:.1f}GB available, {min_space_gb}GB required")
            
            # Cleanup commands
            cleanup_commands = [
                "sudo apt-get clean",
                "sudo apt-get autoremove -y",
                "sudo journalctl --vacuum-time=1d",
                "rm -rf /mnt/data/youtube_auto/venv",  # Remove old venv if exists
                "find ~/.cache -type f -delete"  # Clear user cache
            ]
            
            logger.info("Attempting to free up space...")
            for cmd in cleanup_commands:
                stdin, stdout, stderr = ssh_client.exec_command(cmd)
                logger.info(f"Running cleanup: {cmd}")
                print(stdout.read().decode())
            
            # Check space again
            stdin, stdout, stderr = ssh_client.exec_command("df -h /mnt/data | tail -1 | awk '{print $4}'")
            new_space = stdout.read().decode().strip()
            logger.info(f"Space available after cleanup: {new_space}")
            
            if 'G' in new_space:
                new_space_gb = float(new_space.replace('G', ''))
                if new_space_gb < min_space_gb:
                    raise Exception(f"Insufficient disk space: {new_space_gb:.1f}GB available after cleanup")
            
        return True
    except Exception as e:
        logger.error(f"Error checking disk space: {str(e)}")
        raise

def setup_ec2(ssh_client):
    """Setup Oracle Cloud environment"""
    try:
        # Check disk space first
        check_disk_space(ssh_client)
        
        commands = [
            # Update system
            "sudo apt-get update",
            "sudo apt-get install -y python3-pip python3-venv ffmpeg",
            
            # Setup project directory in /mnt/data
            "sudo mkdir -p /mnt/data/youtube_auto/output/{audio,video,scripts,images}",
            "sudo mkdir -p /mnt/data/youtube_auto/logs",
            "sudo mkdir -p /mnt/data/youtube_auto/credentials",
            "sudo mkdir -p /mnt/data/youtube_auto/tmp",  # Create tmp directory
            
            # Set correct permissions
            "sudo chown -R ubuntu:ubuntu /mnt/data/youtube_auto",
            
            # Create virtual environment
            "cd /mnt/data/youtube_auto && python3 -m venv venv",
            "cd /mnt/data/youtube_auto && source venv/bin/activate && pip install --upgrade pip",
            
            # Install from requirements using the large volume for temp files
            "cd /mnt/data/youtube_auto && source venv/bin/activate && TMPDIR=/mnt/data/youtube_auto/tmp pip install --no-cache-dir -r requirements.txt"
        ]
        
        for cmd in commands:
            logger.info(f"Running: {cmd}")
            stdin, stdout, stderr = ssh_client.exec_command(cmd)
            
            # Stream output in real-time
            while True:
                line = stdout.readline()
                if not line:
                    break
                print(line.strip())
            
            error = stderr.read().decode()
            if error:
                logger.error(f"Error: {error}")
                if "No space left on device" in error:
                    raise Exception("Disk space exhausted during installation")
                
    except Exception as e:
        logger.error(f"Setup failed: {str(e)}")
        raise

def upload_files(ssh_client, username='ubuntu'):
    """Upload necessary files"""
    try:
        # Create remote directory first
        stdin, stdout, stderr = ssh_client.exec_command('sudo mkdir -p /mnt/data/youtube_auto')
        stdin, stdout, stderr = ssh_client.exec_command('sudo chown -R ubuntu:ubuntu /mnt/data/youtube_auto')
        
        sftp = ssh_client.open_sftp()
        local_dir = Path.cwd()
        remote_dir = f"/mnt/data/youtube_auto"
        
        # Files to upload
        files = [
            "main.py",
            "requirements.txt",
            ".env",
            "client_secrets.json",
            "youtube_auto.service"
        ]
        
        # Verify local files exist before uploading
        for file in files:
            local_path = local_dir / file
            remote_path = f"{remote_dir}/{file}"
            
            if local_path.exists():
                logger.info(f"Uploading {file}...")
                sftp.put(str(local_path), remote_path)
                # Set correct permissions
                sftp.chmod(remote_path, 0o644)
            else:
                logger.warning(f"Warning: Local file {file} not found in {local_dir}")
        
        sftp.close()
        logger.info("File upload completed successfully")
        
    except Exception as e:
        logger.error(f"Upload failed: {str(e)}")
        sys.exit(1)

def setup_service(ssh_client):
    """Setup and start the systemd service"""
    commands = [
        "sudo cp /mnt/data/youtube_auto/youtube_auto.service /etc/systemd/system/",
        "sudo systemctl daemon-reload",
        "sudo systemctl enable youtube_auto",
        "sudo systemctl start youtube_auto"
    ]
    
    for cmd in commands:
        stdin, stdout, stderr = ssh_client.exec_command(cmd)
        logger.info(f"Running: {cmd}")
        print(stdout.read().decode())
        print(stderr.read().decode())

def verify_files():
    """Verify all required files exist"""
    required_files = [
        "main.py",
        "requirements.txt",
        ".env",
        "client_secrets.json",
        "youtube_auto.service"
    ]
    
    missing_files = []
    for file in required_files:
        if not Path(file).exists():
            missing_files.append(file)
            logger.error(f"Missing required file: {file}")
    
    if missing_files:
        raise FileNotFoundError(f"Missing required files: {', '.join(missing_files)}")

def main():
    try:
        logger.info("Verifying required files...")
        verify_files()
        
        if len(sys.argv) != 3:
            logger.error("Usage: python deploy.py <key_path> <oracle_ip>")
            sys.exit(1)
        
        key_path = sys.argv[1]
        oracle_ip = sys.argv[2]
        
        logger.info(f"Deploying to Oracle instance: {oracle_ip}")
        ssh_client = connect_to_oracle(key_path, oracle_ip)
        
        try:
            check_disk_space(ssh_client)  # Initial disk space check
            upload_files(ssh_client)
            setup_ec2(ssh_client)
            setup_service(ssh_client)
            logger.info("Deployment successful! 🚀")
            
            # Final space check
            stdin, stdout, stderr = ssh_client.exec_command("df -h /mnt/data | tail -1 | awk '{print $4}'")
            final_space = stdout.read().decode().strip()
            logger.info(f"Final available disk space: {final_space}")
            
        finally:
            ssh_client.close()
            
    except Exception as e:
        logger.error(f"Deployment failed: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()