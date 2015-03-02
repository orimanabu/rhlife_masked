-- references: http://apple.stackexchange.com/questions/78793/apple-script-vpn-textbox
tell application "System Events"
	tell current location of network preferences
		set VPNservice to service "VPN NAME" -- name of the VPN service
		if exists VPNservice then
			if current configuration of VPNservice is not connected then
				connect VPNservice
			else
				error "already connected."
			end if
		end if
	end tell

	do shell script "/PATH/TO/otp.py | pbcopy"

	tell current location of network preferences
		delay 1
		keystroke "v" using command down
		keystroke return

		delay 2
		keystroke return
	end tell
end tell
