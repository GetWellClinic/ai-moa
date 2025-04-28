#!/bin/bash
# Follow AI-MOA logs in real-time
/bin/echo ""
/bin/echo "Watching AI-MOA workflow-incomingfile.logs in realtime..."
/bin/echo "	(To stop watching and exit, press Ctrl-C)"
/bin/echo ""
/usr/bin/journalctl --follow -u ai-moa-incomingfile.service
