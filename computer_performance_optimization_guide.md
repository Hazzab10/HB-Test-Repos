# Computer Performance Optimization Guide

A comprehensive guide to speed up your computer and improve overall system performance.

## Table of Contents
- [Quick Wins](#quick-wins)
- [Startup Optimization](#startup-optimization)
- [Disk & Storage](#disk--storage)
- [Memory Management](#memory-management)
- [Software & Updates](#software--updates)
- [Advanced Optimizations](#advanced-optimizations)
- [Platform-Specific Tips](#platform-specific-tips)

---

## Quick Wins

These actions provide immediate performance improvements with minimal effort:

### 1. Restart Your Computer Regularly
- **Why**: Clears memory leaks, closes orphaned processes, and applies pending updates
- **How Often**: At least once a week for daily-use computers
- **Impact**: High (especially if you haven't restarted in weeks)

### 2. Close Unnecessary Browser Tabs
- **Why**: Each tab consumes RAM and CPU resources
- **Tip**: Use browser extensions like "The Great Suspender" or "OneTab"
- **Impact**: Medium to High (browsers are often the biggest memory hogs)

### 3. Check for Malware/Viruses
- **Tools**:
  - Windows: Windows Defender (built-in), Malwarebytes
  - Mac: Malwarebytes for Mac
  - Linux: ClamAV
- **Impact**: Very High (if infected)

### 4. Update Your Operating System
- **Why**: Updates include performance improvements and bug fixes
- **How**: Enable automatic updates for security patches
- **Impact**: Medium

---

## Startup Optimization

Reducing startup programs dramatically improves boot time and frees up resources.

### Windows

1. **Open Task Manager**
   - Press `Ctrl + Shift + Esc`
   - Click "Startup" tab

2. **Disable Unnecessary Programs**
   - Right-click programs you don't need at startup
   - Select "Disable"
   - Common culprits: Adobe updaters, cloud sync clients, messaging apps

3. **Check Startup Impact**
   - Task Manager shows "Startup impact" (High/Medium/Low)
   - Prioritize disabling "High" impact items

### Mac

1. **System Preferences → Users & Groups**
2. **Click your username → Login Items**
3. **Remove unnecessary apps** with the "-" button
4. **Alternative**: Use `sudo launchctl list` in Terminal to see all launch agents

### Linux

1. **Check startup applications**
   ```bash
   # For systemd-based systems
   systemctl list-unit-files --state=enabled

   # Disable a service
   sudo systemctl disable service-name
   ```

2. **GUI Method**
   - Most desktop environments have a "Startup Applications" manager
   - GNOME: `gnome-session-properties`
   - KDE: System Settings → Startup and Shutdown

---

## Disk & Storage

### Free Up Disk Space

**Critical**: Keep at least 10-20% of your disk free for optimal performance.

#### Windows

1. **Disk Cleanup**
   - Search "Disk Cleanup" in Start menu
   - Select drive (usually C:)
   - Check all boxes, especially "Temporary files"
   - Click "Clean up system files" for additional options

2. **Storage Sense** (Windows 10/11)
   - Settings → System → Storage
   - Enable "Storage Sense" for automatic cleanup
   - Configure to run weekly/monthly

3. **Clear Windows Update Cache**
   ```cmd
   # Run as Administrator
   net stop wuauserv
   del /f /s /q C:\Windows\SoftwareDistribution\*
   net start wuauserv
   ```

4. **Find Large Files**
   - Use tools like WinDirStat or TreeSize Free
   - Visualize disk usage and identify space hogs

#### Mac

1. **Storage Management**
   - Apple menu → About This Mac → Storage → Manage
   - Options: Optimize Storage, Empty Trash Automatically

2. **Clear Cache**
   ```bash
   # User cache
   rm -rf ~/Library/Caches/*

   # System cache (requires sudo)
   sudo rm -rf /Library/Caches/*
   ```

3. **Find Large Files**
   ```bash
   # Find files larger than 1GB
   find ~ -type f -size +1G
   ```

#### Linux

1. **Clean Package Cache**
   ```bash
   # Debian/Ubuntu
   sudo apt-get clean
   sudo apt-get autoclean
   sudo apt-get autoremove

   # Fedora/RHEL
   sudo dnf clean all

   # Arch
   sudo pacman -Sc
   ```

2. **Find Large Files**
   ```bash
   # Find 100 largest files in home directory
   du -ah ~ | sort -rh | head -n 100

   # Disk usage by directory
   du -h --max-depth=1 ~ | sort -rh
   ```

3. **Clear Journal Logs**
   ```bash
   # Limit journal size to 500MB
   sudo journalctl --vacuum-size=500M
   ```

### Disk Defragmentation (HDD Only)

**⚠️ DO NOT defragment SSDs** - it reduces their lifespan and provides no benefit.

#### Windows (HDD)
- Search "Defragment and Optimize Drives"
- Select drive → Analyze → Optimize
- Schedule weekly/monthly optimization

#### Mac
- macOS automatically defragments files under 20MB
- For larger files, use third-party tools (rarely needed)

#### Linux (HDD)
```bash
# Check fragmentation (ext4)
sudo e4defrag -c /dev/sdX

# Defragment (if needed)
sudo e4defrag /dev/sdX
```

---

## Memory Management

### Monitor Memory Usage

#### Windows
1. **Task Manager** (`Ctrl + Shift + Esc`)
   - Performance tab → Memory
   - Processes tab → Sort by Memory
   - Identify and close memory-hungry applications

2. **Resource Monitor**
   - Search "Resource Monitor"
   - Memory tab for detailed analysis

#### Mac
1. **Activity Monitor** (`Cmd + Space` → "Activity Monitor")
   - Memory tab
   - Sort by Memory column
   - Check "Memory Pressure" graph (green = good, red = bad)

#### Linux
```bash
# Current memory usage
free -h

# Real-time process monitoring
htop  # (install if not available)

# Detailed memory info
cat /proc/meminfo
```

### Increase Virtual Memory (Swap)

#### Windows
1. System Properties → Advanced → Performance Settings
2. Advanced tab → Virtual Memory → Change
3. Custom size:
   - Initial: 1.5x your RAM
   - Maximum: 3x your RAM
4. Example for 8GB RAM: Initial 12GB, Max 24GB

#### Linux
```bash
# Check current swap
swapon --show

# Create swap file (4GB example)
sudo fallocate -l 4G /swapfile
sudo chmod 600 /swapfile
sudo mkswap /swapfile
sudo swapon /swapfile

# Make permanent (add to /etc/fstab)
echo '/swapfile none swap sw 0 0' | sudo tee -a /etc/fstab
```

### Reduce Memory Usage

1. **Close unused applications**
2. **Use lightweight alternatives**:
   - Browser: Firefox/Edge instead of Chrome (for memory)
   - Text editor: Notepad++/gedit instead of full IDEs
   - PDF reader: Sumatra PDF instead of Adobe Reader
3. **Limit browser extensions** - each uses memory
4. **Adjust visual effects** (Windows: Performance Options → "Adjust for best performance")

---

## Software & Updates

### Keep Software Updated

1. **Operating System**: Enable automatic security updates
2. **Drivers**:
   - Windows: Use Windows Update or manufacturer utilities
   - Mac: Updates included in system updates
   - Linux: Usually included in package updates

3. **Graphics Drivers**: Critical for performance
   - NVIDIA: GeForce Experience
   - AMD: Amd Software
   - Intel: Intel Driver & Support Assistant

### Remove Bloatware & Unused Programs

#### Windows
1. **Settings → Apps → Apps & Features**
2. **Sort by size** to find large programs
3. **Uninstall** programs you don't use
4. **Use tools**: Revo Uninstaller (removes leftover files)

#### Mac
1. **Finder → Applications**
2. **Drag unwanted apps to Trash**
3. **Use AppCleaner** to remove associated files

#### Linux
```bash
# List installed packages by size (Debian/Ubuntu)
dpkg-query -Wf '${Installed-Size}\t${Package}\n' | sort -rn | head -n 20

# Remove package
sudo apt-get remove package-name
sudo apt-get purge package-name  # Also removes config files
```

### Disable Unnecessary Services

#### Windows
1. **Services** (search in Start menu)
2. **Common services to disable**:
   - Windows Search (if you don't use search)
   - Print Spooler (if no printer)
   - Bluetooth Support Service (if not using Bluetooth)
   - Remote Registry
3. **Right-click → Properties → Startup type → Disabled**

**⚠️ Warning**: Only disable services you understand.

---

## Advanced Optimizations

### Enable Hardware Acceleration

1. **Browser**: Settings → Advanced → System → "Use hardware acceleration"
2. **Applications**: Check video players, photo editors, etc.
3. **Windows**: Settings → Display → Graphics settings → Hardware-accelerated GPU scheduling

### Adjust Power Settings

#### Windows
1. **Control Panel → Power Options**
2. **Select "High Performance" plan** (for desktops)
3. **For laptops**: Create custom plan balancing performance and battery

#### Mac
1. **System Preferences → Energy Saver**
2. **Prevent computer from sleeping** (during intensive tasks)
3. **Disable Power Nap** if experiencing slowdowns

#### Linux
```bash
# Install TLP (laptop power management)
sudo apt-get install tlp

# For performance (desktops)
sudo cpupower frequency-set -g performance
```

### Optimize Browser Performance

1. **Clear browsing data regularly**:
   - Cache, cookies, download history
   - Chrome/Edge: `Ctrl + Shift + Del`
   - Firefox: `Ctrl + Shift + Del`

2. **Disable unnecessary extensions**
3. **Enable prefetching** (Chrome: chrome://settings/privacy → "Preload pages")
4. **Use ad blocker** (reduces page load time and memory)

### Check Thermals (Overheating)

Overheating causes thermal throttling, reducing performance.

1. **Clean dust from fans and vents**
2. **Monitor temperatures**:
   - Windows: HWMonitor, Core Temp
   - Mac: Macs Fan Control, iStat Menus
   - Linux: `sensors` command (install lm-sensors)

3. **Acceptable ranges**:
   - CPU idle: 30-50°C
   - CPU load: 60-80°C
   - GPU idle: 30-45°C
   - GPU load: 65-85°C

4. **If overheating**:
   - Reapply thermal paste (advanced)
   - Improve case airflow
   - Use laptop cooling pad

### Upgrade Hardware

When software optimizations aren't enough:

1. **RAM** (biggest impact for multitasking)
   - Minimum: 8GB
   - Recommended: 16GB
   - Power users: 32GB+

2. **SSD** (dramatic improvement over HDD)
   - Boot time: HDD 1-2min → SSD 10-30sec
   - Application load: 2-5x faster
   - Overall responsiveness: Night and day difference

3. **Graphics Card** (for gaming/video editing)
4. **CPU** (expensive, least cost-effective)

**ROI Priority**: SSD > RAM > GPU > CPU

---

## Platform-Specific Tips

### Windows Only

1. **Disable Windows Tips & Suggestions**
   - Settings → System → Notifications & actions

2. **Turn Off Background Apps**
   - Settings → Privacy → Background apps

3. **Disable Transparency Effects**
   - Settings → Personalization → Colors → Transparency effects

4. **Adjust Visual Effects**
   - System Properties → Advanced → Performance Settings
   - "Adjust for best performance" or custom

5. **Registry Cleanup** (Advanced)
   - Use CCleaner or similar (backup registry first)

6. **Disable Cortana** (if unused)
   - Group Policy or Registry edit

### Mac Only

1. **Reduce Transparency**
   - System Preferences → Accessibility → Display → Reduce transparency

2. **Disable Dashboard** (older macOS)
   ```bash
   defaults write com.apple.dashboard mcx-disabled -boolean TRUE
   killall Dock
   ```

3. **Limit Spotlight Indexing**
   - System Preferences → Spotlight → Privacy
   - Add folders to exclude from indexing

4. **Reset SMC & NVRAM** (when experiencing issues)
   - SMC: Power troubleshooting
   - NVRAM: Settings and startup

5. **Use Activity Monitor**
   - Identify apps with high "Energy Impact"

### Linux Only

1. **Use Lightweight Desktop Environment**
   - XFCE, LXDE, or LXQt instead of GNOME/KDE
   - Can cut RAM usage by 50%+

2. **Disable Unnecessary Daemons**
   ```bash
   systemctl list-unit-files --state=enabled
   ```

3. **Adjust Swappiness**
   ```bash
   # Check current value
   cat /proc/sys/vm/swappiness

   # Set to 10 (default is 60, lower = less swapping)
   sudo sysctl vm.swappiness=10

   # Make permanent
   echo 'vm.swappiness=10' | sudo tee -a /etc/sysctl.conf
   ```

4. **Use Preload** (predicts and preloads apps)
   ```bash
   sudo apt-get install preload
   ```

5. **Optimize SSD (TRIM)**
   ```bash
   # Check TRIM support
   sudo hdparm -I /dev/sda | grep TRIM

   # Enable weekly TRIM
   sudo systemctl enable fstrim.timer
   ```

---

## Performance Monitoring Checklist

Use this checklist weekly/monthly to maintain optimal performance:

### Weekly
- [ ] Restart computer
- [ ] Close unused browser tabs
- [ ] Check for OS updates
- [ ] Clear browser cache
- [ ] Empty recycle bin/trash
- [ ] Check available disk space (>15% free)

### Monthly
- [ ] Run antivirus/malware scan
- [ ] Review startup programs
- [ ] Uninstall unused software
- [ ] Clear temporary files
- [ ] Check for driver updates
- [ ] Review running background processes
- [ ] Defragment HDD (if applicable)

### Quarterly
- [ ] Deep clean disk (large files, duplicate files)
- [ ] Review and disable unnecessary services
- [ ] Check system temperatures
- [ ] Physical cleaning (dust removal)
- [ ] Backup important data
- [ ] Consider hardware upgrades if needed

### Performance Indicators

**Your computer needs attention if**:
- Boot time > 2 minutes (HDD) or > 1 minute (SSD)
- Applications take > 10 seconds to launch
- Frequent freezing or "not responding" errors
- Disk usage constantly at 100% (Task Manager)
- Memory usage > 90% during normal use
- CPU temperature > 85°C under load
- Fans constantly running at high speed

---

## Troubleshooting Specific Issues

### "Disk Usage at 100%"

1. Disable Windows Search temporarily
2. Check for Windows updates being downloaded
3. Scan for malware
4. Check for failing hard drive (CrystalDiskInfo)

### "High CPU Usage"

1. Check Task Manager for specific process
2. Restart the problematic application
3. Update or reinstall the application
4. Check for malware
5. Verify CPU temperatures (may be throttling)

### "Computer Slow After Update"

1. Wait 24 hours (indexing and optimization)
2. Check Windows Update for additional patches
3. Review new startup programs
4. Consider rolling back update (if critical issue)

### "Browser Very Slow"

1. Clear cache and cookies
2. Disable extensions one-by-one
3. Reset browser settings
4. Try different browser
5. Check for DNS issues (try 8.8.8.8 or 1.1.1.1)

---

## Quick Reference: Commands

### Windows (Command Prompt/PowerShell)

```cmd
# System information
systeminfo

# Check disk
chkdsk C: /f

# Clear DNS cache
ipconfig /flushdns

# Check network statistics
netstat -an

# Temperature & hardware (requires third-party tools)
# Use: HWMonitor, Core Temp, GPU-Z
```

### Mac (Terminal)

```bash
# System information
system_profiler SPHardwareDataType

# Disk usage
df -h

# Purge RAM
sudo purge

# Check disk errors
diskutil verifyVolume /

# Network reset
sudo dscacheutil -flushcache
sudo killall -HUP mDNSResponder
```

### Linux (Terminal)

```bash
# System information
uname -a
lscpu
lsmem

# Disk usage
df -h
du -sh /*

# Memory info
free -h

# Process monitoring
htop
top

# Disk health
sudo smartctl -a /dev/sda

# Network stats
ss -tuln
```

---

## Additional Resources

### Tools

**Monitoring & Diagnostics**:
- CPU-Z / GPU-Z (Windows)
- HWMonitor (Windows)
- Crystal Disk Info (disk health)
- LatencyMon (Windows latency issues)

**Cleanup**:
- CCleaner (multi-platform)
- BleachBit (multi-platform, open-source)
- WinDirStat / WizTree (Windows)
- DaisyDisk / GrandPerspective (Mac)

**Performance**:
- MSI Afterburner (GPU monitoring/tuning)
- ThrottleStop (CPU undervolting, advanced)
- Razer Cortex / Game Fire (gaming optimization)

### Learning Resources

- Microsoft: "Performance Information and Tools"
- Apple Support: "How to speed up a slow Mac"
- /r/techsupport (Reddit community)
- /r/buildapc (hardware advice)

---

## Summary: Top 10 Actions

If you only do 10 things, do these:

1. ✅ **Restart your computer weekly**
2. ✅ **Disable unnecessary startup programs**
3. ✅ **Keep 15-20% disk space free**
4. ✅ **Run regular malware scans**
5. ✅ **Update your OS and drivers**
6. ✅ **Close unused browser tabs/extensions**
7. ✅ **Uninstall unused programs**
8. ✅ **Clean dust from vents and fans**
9. ✅ **Monitor system temperatures**
10. ✅ **Upgrade to SSD if still using HDD** (hardware)

---

**Remember**: Performance optimization is about maintaining good habits. Set calendar reminders for weekly/monthly tasks to keep your computer running smoothly!

**Last Updated**: 2026-01-19
