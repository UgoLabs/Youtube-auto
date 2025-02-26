import os
import sys
import subprocess
import paramiko
import logging
from pathlib import Path
import zipfile
import io

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def connect_to_ec2(key_path, ec2_ip, username='ubuntu'):
    """Connect to EC2 instance"""
    try:
        logger.info(f"Connecting to EC2 instance at {ec2_ip}")
        key = paramiko.RSAKey.from_private_key_file(key_path)
        client = paramiko.SSHClient()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        client.connect(ec2_ip, username=username, pkey=key)
        logger.info("Successfully connected to EC2")
        return client
    except Exception as e:
        logger.error(f"Failed to connect to EC2: {str(e)}")
        sys.exit(1)

def upload_all_files(ssh_client, username='ubuntu'):
    """Upload all project files and directories"""
    try:
        logger.info("Preparing to upload all project files...")
        
        # Create zip file in memory
        logger.info("Creating zip archive of project files...")
        zip_buffer = io.BytesIO()
        
        with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
            # Get all files in current directory and subdirectories
            for root, dirs, files in os.walk('.'):
                if '.git' in root or 'venv' in root or '__pycache__' in root:
                    continue
                    
                for file in files:
                    if file.endswith('.pyc'):
                        continue
                        
                    full_path = os.path.join(root, file)
                    arcname = os.path.relpath(full_path, '.')
                    logger.info(f"Adding to zip: {arcname}")
                    zip_file.write(full_path, arcname)
        
        # Reset buffer position
        zip_buffer.seek(0)
        
        # Create remote directories
        logger.info("Creating remote directories...")
        cmds = [
            'sudo mkdir -p /mnt/data/youtube_auto',
            'sudo chown -R ubuntu:ubuntu /mnt/data/youtube_auto',
            'mkdir -p /mnt/data/youtube_auto/utils',
            'mkdir -p /mnt/data/youtube_auto/agent',
            'mkdir -p /mnt/data/youtube_auto/output/{scripts,audio,images,videos}',
            'mkdir -p /mnt/data/youtube_auto/logs',
            'mkdir -p /mnt/data/youtube_auto/credentials'
        ]
        
        for cmd in cmds:
            stdin, stdout, stderr = ssh_client.exec_command(cmd)
        
        # Upload zip file
        logger.info("Uploading project archive...")
        sftp = ssh_client.open_sftp()
        sftp.putfo(zip_buffer, '/mnt/data/youtube_auto/project.zip')
        
        # Extract files on remote server
        logger.info("Extracting files on remote server...")
        stdin, stdout, stderr = ssh_client.exec_command('cd /mnt/data/youtube_auto && unzip -o project.zip')
        stdout.read()  # Wait for command to complete
        
        # Remove zip file
        ssh_client.exec_command('rm /mnt/data/youtube_auto/project.zip')
        
        logger.info("Project files uploaded successfully")
        sftp.close()
        
    except Exception as e:
        logger.error(f"Project upload failed: {str(e)}")
        sys.exit(1)

def main():
    try:
        if len(sys.argv) != 3:
            logger.error("Usage: python deploy_fix.py <key_path> <ec2_ip>")
            sys.exit(1)
        
        key_path = sys.argv[1]
        ec2_ip = sys.argv[2]
        
        logger.info(f"Connecting to EC2 instance: {ec2_ip}")
        ssh_client = connect_to_ec2(key_path, ec2_ip)
        
        try:
            # Upload all project files
            upload_all_files(ssh_client)
            
            # Install unzip if needed
            ssh_client.exec_command('sudo apt-get install -y unzip')
            
            # Restart the service
            commands = [
                "sudo systemctl daemon-reload",
                "sudo systemctl restart youtube_auto"
            ]
            
            for cmd in commands:
                stdin, stdout, stderr = ssh_client.exec_command(cmd)
                logger.info(f"Running: {cmd}")
                print(stdout.read().decode())
            
            logger.info("Project files uploaded and service restarted! 🚀")
            
        finally:
            ssh_client.close()
            
    except Exception as e:
        logger.error(f"Deployment failed: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()