#!/bin/bash

i18n_pot_files=$(ls *-generated.pot)
i18n_en_files=$(ls *-en.po)


default=''
for pot in $i18n_pot_files; do
    po_file=${pot//-generated.pot/-en.generated}
    po_head=${pot//-generated.pot/-en.header}

    mv -f "$po_file" "$po_file~"
    cat "$po_head" > $po_file
    cat "$pot" | while read line; do

	if echo $line | grep '#. Default: ' &>/dev/null; then
	    default=$(echo $line | grep '#. Default: ' | cut -d'"' -f2)
	fi
	
	test ! -z "$default" && {
	
	    if echo $line | grep 'msgstr' &>/dev/null; then
		echo "msgstr \"$default\"" >> $po_file
		echo >> $po_file
		default=''

	    else
		echo "$line" >> $po_file
	    fi
	
	}

    done
done
