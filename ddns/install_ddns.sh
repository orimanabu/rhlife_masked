#!/bin/sh

cp com.redhat.update-ddns.plist ~/Library/LaunchAgents/
launchctl load ~/Library/LaunchAgents/com.redhat.update-ddns.plist
