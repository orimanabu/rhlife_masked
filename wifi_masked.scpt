-- inspired by: http://forums.macrumors.com/showthread.php?t=1099181
tell application "System Events"
	tell process "SystemUIServer"
		tell menu bar 1
			set menuExtras to (value of attribute "AXChildren")
			set airport to -1
			repeat with aMenu in menuExtras
				tell aMenu
					if value of attribute "AXDescription" contains "Wi-Fi" then
						set airport to aMenu
						exit repeat
					end if
				end tell
			end repeat
			
			if airport is -1 then
				display dialog "Could not find Menu Extra"
				return
			else
				tell airport
					perform action "AXPress"
					tell menu 1
						click menu item "ほかのネットワークに接続..."
					end tell
				end tell
			end if
		end tell
		
		tell window 1
			delay 0.1 -- wait for dialog to open
			keystroke "SSID"
			tell pop up button 1
				click
				click menu item "WPA2 エンタープライズ" of menu 1
				delay 0.1 -- wait for password field to appear
				keystroke "USERNAME"
				keystroke tab
				do shell script "/path/to/otp.py | pbcopy"
				keystroke "v" using command down
				-- keystroke tab
				-- keystroke tab
				-- keystroke space
				keystroke return
			end tell
		end tell
	end tell
end tell
