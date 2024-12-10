# Installing GPU Driver

To enable GPU support for the application, follow the steps below to install the NVIDIA GPU driver. This guide assumes you're using an NVIDIA GPU and Linux-based system (e.g., Ubuntu). 

## Steps to Install GPU Driver

### 1. Find the Recommended Driver

- Identify your GPU model.
- Go to the [NVIDIA driver download page](https://www.nvidia.com/).
- Select the appropriate GPU card and operating system version.
- For example, if you have a **NVIDIA** card, you may need the driver version `NVIDIA-Linux-x86_64-550.78` (or a later version).
  
Make sure to download the correct driver version that matches your GPU model.

### 2. Download the Driver

Once you have identified the right driver version for your GPU, download the **NVIDIA driver** installer package (e.g., `NVIDIA-Linux-x86_64-550.78.run`) to your system.

### 3. Install the GPU Driver

After downloading the driver, follow the steps below to install it:

1. **Give execute permission** to the downloaded installer:

   `chmod +x NVIDIA-Linux-x86_64-550.78.run`

2. **Run the installation:**
   
   `sudo ./NVIDIA-Linux-x86_64-550.78.run`

3. Follow the on-screen instructions to complete the installation.

### 4. Troubleshooting Installation Issues

If you encounter issues during installation, check the logs for specific error messages. Common issues may include:

Compiler Issues: Sometimes, the installation may fail due to an outdated compiler. 

In such cases:

Update the compiler (e.g., gcc and g++).

### 5. Verify Installation Using nvidia-smi
Once the driver is successfully installed, you can verify that the GPU is being used by running:

`nvidia-smi`

This will display information about your GPU, including its current usage, temperature, and active processes. If everything is set up correctly, you should see the GPU listed in the output.