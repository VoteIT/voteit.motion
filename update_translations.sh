 #!/bin/bash
 #You need lingua and gettext installed to run this
 
 echo "Updating voteit.motion.pot"
 pot-create -d voteit.motion -o voteit/motion/locale/voteit.motion.pot .
 echo "Merging Swedish localisation"
 msgmerge --update voteit/motion/locale/sv/LC_MESSAGES/voteit.motion.po voteit/motion/locale/voteit.motion.pot
 echo "Updated locale files"
 