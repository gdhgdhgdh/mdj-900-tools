# mdj-900-tools
Gemini Sound MDJ CDJ DJ Media Player tools

## Introduction

I wanted to learn how to DJ using 'CDJ's but the market monopoly of Pioneer DJ means that genuine CDJ equipment is extremely expensive, especially when two units are involved. Instead, I chose a copycat device from [Gemini Sound](https://geminisound.com) called the [MDJ-900](https://geminisound.com/products/mdj-900). These are based on Linux 2.6 kernel and implement a similar network approach that Pioneer DJ units do, i.e. you can connect them to their own network switch and share a single USB stick across all of the MDJ players. Additionally you can define one player to provide 'master sync' and any client players will follow the tempo.

Since I love tinkering with systems, I wanted to achieve three things:

 - Remove the need to use a USB stick - instead allow a computer to act as a music server
 - The MDJ supports AAC/MP3/WAV/AIFF files. Most of my collection is FLAC, so I want the music server to transcode FLAC -> WAV
 - Support the native 'Playlist' format of the MDJ series so it's easier to work with industry standard tools like Serato


## Protocol

These are brief notes to aid my memory rather than a full write-up.
 - Each MDJ will get a random MAC address at boot
 - No DHCP address is requested - each MDJ will choose a random autoconf address in 169.254.x.x/16
 - Each MDJ sends out two UDP heartbeat packets to 169.254.255.255 port 6996 every 2-3 seconds. The SOURCE PORT of these broadcasts is mathematically linked to the source IP address, via a currently-unknown mechanism.
   - e.g. IP 169.254.175.49 MUST use source port 35756 or MDJ's in the network will not acknowledge the server's existence
 - If it's been eight seconds since the last heartbeat, the MDJ will go into 'offline' / emergency loop mode
 - The contents of those heartbeat packets are mostly blank with a few magic values, and some reverse-engineered values
 - The MDJ's are Linux-based and use NFS v3 to share the USB stick - the mountpoint is typically '/tmp/0' but can be changed provided it's not longer than seven (!) characters
 
## Usage

I use a Mac, so I needed to set up the NFS server. This was mercifully simple.

 - Manually set the IP address of your Mac to be 169.254.175.49 with netmask 255.255.0.0 - it must be precisely this IP address + netmask!
    - You might want to use an extra USB network adapter so you don't lose Internet access
 - Copy a bunch of MP3s into a new directory `/opt/0`
 - Create `/etc/exports` with the following single line `/opt/0 -mapall=501`
 - run `nfsd start`
 - run `showmount -e` to verify that path is being exported
 - run `python server.py`
 - Power up an MDJ unit and press the 'Link' button on the right. It will stay at 'CONNECTING' for about 10 seconds before showing a waveform.

## Issues

 - The gemini sqlite database is not being read correctly - per-track BPM is not set!
 - Takes much longer to join the Link group then when using two MDJ's on a private network

## Todo
 - Virtual NFS server
 - Transcode file formats
 - Serato Playlists / Crate conversion



find ../*mp3 -print0 | xargs -0 -n 1 python3 ~/mdj-900-tools/update_geminidb.py
