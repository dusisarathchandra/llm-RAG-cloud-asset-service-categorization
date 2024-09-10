# Docker Compose Installation Guide

This guide provides instructions for installing Docker Compose on Linux, Windows, and macOS.

## Linux

1. Run this command to download the current stable release of Docker Compose:

   ```
   sudo curl -L "https://github.com/docker/compose/releases/download/1.29.2/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
   ```

2. Apply executable permissions to the binary:

   ```
   sudo chmod +x /usr/local/bin/docker-compose
   ```

3. Verify the installation:

   ```
   docker-compose --version
   ```

## Windows

1. Install Docker Desktop for Windows:
   - Download Docker Desktop from the [official Docker website](https://www.docker.com/products/docker-desktop)
   - Double-click the installer to run it
   - Follow the installation wizard

2. Docker Compose is included with Docker Desktop for Windows, so no additional steps are required.

3. Verify the installation by opening a command prompt and running:

   ```
   docker-compose --version
   ```

## macOS

1. Install Docker Desktop for Mac:
   - Download Docker Desktop from the [official Docker website](https://www.docker.com/products/docker-desktop)
   - Double-click the `.dmg` file to open it
   - Drag the Docker icon to the Applications folder

2. Docker Compose is included with Docker Desktop for Mac, so no additional steps are required.

3. Verify the installation by opening a terminal and running:

   ```
   docker-compose --version
   ```

## Updating Docker Compose

### Linux

To update Docker Compose on Linux, download the latest version and replace the existing one:

```
sudo curl -L "https://github.com/docker/compose/releases/download/1.29.2/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
```

Replace `1.29.2` with the latest version number.

### Windows and macOS

On Windows and macOS, Docker Compose is updated automatically when you update Docker Desktop.

## Uninstalling Docker Compose

### Linux

To uninstall Docker Compose on Linux:

```
sudo rm /usr/local/bin/docker-compose
```

### Windows and macOS

Uninstalling Docker Desktop will also remove Docker Compose.

Remember to check the [official Docker documentation](https://docs.docker.com/compose/install/) for the most up-to-date installation instructions and version numbers.
