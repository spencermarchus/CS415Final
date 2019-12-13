# CS415Final

Step-by-Step Instructions to Run Application
The directions to run the program are as follows. You will have issues if you do not. . .

These directions are given in our submission as well - they may be easier to read there.

Ghostscript is a dependency which enables saving Tkinter canvases to .png files. 
On Windows, install Ghostscript and add the “C:\Program Files\gs\gs9.50\bin” folder to your PATH environment variable on computers that will act as peers.
(Verify the actual installation directory, as it may vary)
https://www.ghostscript.com/download/gsdnld.html

Unfortunately, we do not know of the install procedure for Ubuntu or MacOS as we have not tested this. While we expect it to still work, we just don’t know the exact installation instructions.

Ensure that you have Python 3+ installed and added to your PATH if on Windows, so that Windows can know what to do when “python peer.py” is called. 

Windows computers without python installed can run the .exe files in the “dist” folder using the “run ___ exe.bat” files, but then you would not be able to re-build new .exe files if you modify the sources.

Start the server.py file (using “start server.bat” or “start server exe.bat” on a Windows machine) on a computer whose IP address is known - the Peers will connect using port 9998. If the server is not on your LAN, you MUST have port forwarding of TCP port 9998 enabled.

While the server and peer files both listen and try to connect using 127.0.0.1 (localhost) as a last resort / backup option, this should not be relied upon. You will enter the server’s IP address in a GUI when you launch your peers.
Note - In general, one can also run this file from the command line by simply executing “python3 server” in a terminal. No arguments are necessary.

NOTE: You will need at least two Peers and a server running with both peers connected to this server to run the program in a meaningful way. This can all be done on one machine or on separate machines - whatever you wish. If all are run on the same machine, the Peers and Server will communicate via localhost and run in LAN mode. At this time, it is not supported to host a server and operate in INTERNET mode at the same time, as port forwarding would be required for outside peers to connect.

From this point, you have two options. Either you can run our included peer.exe file on a Windows machine and skip to step 8 (which eliminates the need for using pip to install dependencies) and run the program, or you can continue on to step 6 and run our code from source. 

If you choose to run the program from the source code, you will need to run “install dependencies.bat” which uses pip to install dependencies that the program relies on. If you are not on a Windows machine, simply view the contents of this file to view the dependencies you must install via pip on the command line.

Now, you should be able to launch the peer using “start peer.bat”

Enter a nickname for yourself, as well as the IP of the server. If you are running it locally, simply enter 127.0.0.1 in this field. Clicking the “Host Server” option would eliminate the need to launch the server separately in step 4.

Interact with the program!

If any of this was too confusing - feel free to reach out to spencer.marchus@ndsu.edu for clarification / help running the program as he has had the most experience configuring this. Thanks!


-Spencer, McKenna, Cameron, and Jack











COPYRIGHT:

Use of ttkThemes and tkinter is authorized by the following license terms:

Tcl/Tk License Terms
This software is copyrighted by the Regents of the University of California, Sun Microsystems, Inc., Scriptics Corporation, and other parties. The following terms apply to all files associated with the software unless explicitly disclaimed in individual files.

The authors hereby grant permission to use, copy, modify, distribute, and license this software and its documentation for any purpose, provided that existing copyright notices are retained in all copies and that this notice is included verbatim in any distributions. No written agreement, license, or royalty fee is required for any of the authorized uses. Modifications to this software may be copyrighted by their authors and need not follow the licensing terms described here, provided that the new terms are clearly indicated on the first page of each file where they apply.

IN NO EVENT SHALL THE AUTHORS OR DISTRIBUTORS BE LIABLE TO ANY PARTY FOR DIRECT, INDIRECT, SPECIAL, INCIDENTAL, OR CONSEQUENTIAL DAMAGES ARISING OUT OF THE USE OF THIS SOFTWARE, ITS DOCUMENTATION, OR ANY DERIVATIVES THEREOF, EVEN IF THE AUTHORS HAVE BEEN ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

THE AUTHORS AND DISTRIBUTORS SPECIFICALLY DISCLAIM ANY WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE, AND NON-INFRINGEMENT. THIS SOFTWARE IS PROVIDED ON AN "AS IS" BASIS, AND THE AUTHORS AND DISTRIBUTORS HAVE NO OBLIGATION TO PROVIDE MAINTENANCE, SUPPORT, UPDATES, ENHANCEMENTS, OR MODIFICATIONS.

GOVERNMENT USE: If you are acquiring this software on behalf of the U.S. government, the Government shall have only "Restricted Rights" in the software and related documentation as defined in the Federal Acquisition Regulations (FARs) in Clause 52.227.19 (c) (2). If you are acquiring the software on behalf of the Department of Defense, the software shall be classified as "Commercial Computer Software" and the Government shall have only "Restricted Rights" as defined in Clause 252.227-7013 (c) (1) of DFARs. Notwithstanding the foregoing, the authors grant the U.S. Government and others acting in its behalf permission to use and distribute the software in accordance with the terms specified in this license.