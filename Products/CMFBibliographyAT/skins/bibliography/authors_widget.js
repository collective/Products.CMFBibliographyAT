function removeFieldRow(node){

    // XXX replace with getParentElement
    row = node.parentNode.parentNode;
    row.parentNode.removeChild(row);

    return;
}


function handleKeyPress (e) {
    /* Dispatcher for handling the last row */

    // XXX: Generalize window.event for windows
    // Grab current node, replicate, remove listener, append
    var currnode = window.event ? window.event.srcElement : e.currentTarget;
    /* 
       XXX Should add/remove event listeners via JS, but IE has
       non-standard methods.  Not hard, but for now, just check 
       if we are the last row.  If not, bail.
    */

    /* Use from search widget */
    var tbody = getParentElement(currnode, "TBODY");
    var tr = getParentElement(currnode, "TR");
    var rows = tbody.getElementsByTagName("TR");

    if (rows.length == (tr.rowIndex)) {
    	// Add all the last row specific stuff here
    	var newtr = tr.cloneNode(true);

    	now = new Date();
    	id = now.getTime();
    	
    	newtr.id = id

    	// Turn on hidden "delete" image for current node
    	for (var i = 0; (img = tr.getElementsByTagName("IMG").item(i)); i++) {
        	img.style.display = "inline";
        }

        // Look up and modify the id of the input and span elements
        // Id prefixes is everything before _
        var xre = new RegExp(/^[a-zA-Z0-9]+_/)
        for (var c = 0; (cell = newtr.getElementsByTagName('INPUT').item(c)); c++) {
            if (cell.getAttribute('id')) {
                cell.setAttribute('id', xre.exec(cell.id) + id)
            }
        }

        for (var c = 0; (cell = newtr.getElementsByTagName('SPAN').item(c)); c++) {
            if (cell.getAttribute('id')) {
                cell.setAttribute('id', xre.exec(cell.id) + id)
            }
        }

        tr.parentNode.appendChild(newtr);
        // Update ordering after adding, the DOM tree moves in mysterous ways
        // updateOrderIndex(tbody)

    } else {
	// Handle all other keypress entries, like cursor keys
    }

    return;
}


function getParentElement(currnode, tagname) {
    /* Recursive function to move up the tree to a certain parent */

    tagname = tagname.toUpperCase();
    var parent = currnode.parentNode;

    while (parent.tagName.toUpperCase() != tagname) {
    	parent = parent.parentNode;
	    // Next line is a safety belt
	    if (parent.tagName.toUpperCase == "BODY") return null;
    }

    return parent;
}


function moveRowDown(node){
    var row = getParentElement(node, "TR")
    var tbody = getParentElement(row, "TBODY");
    var rows = tbody.getElementsByTagName('TR')
    var idx = null
    // We can't use nextSibling because of blank text nodes in some browsers
    // Need to find the index of the row
    for (var t = 0; (r = rows.item(t)); t++) {
        if (r == row) {
            idx = t
        }
    }
    // idx+2 due to the blank bottom row always being at the bottom
    if ((idx != null) && (rows.length > (idx+2))) {
        var nextRow = rows.item(idx+1)
        shiftRow(nextRow, row)
        //updateOrderIndex(tbody)
        //if (nextRow && (rows.length != (nextRow.rowIndex))){
        //    shiftRow(nextRow, row)
        //}
    }
}
function moveRowUp(node){
    var row = getParentElement(node, "TR")
    var tbody = getParentElement(row, "TBODY");
    var rows = tbody.getElementsByTagName('TR')
    var idx = null
    // We can't use nextSibling because of blank text nodes in some browsers
    // Need to find the index of the row
    for (var t = 0; (r = rows.item(t)); t++) {
        if (r == row) {
            idx = t
        }
    }

    if ((idx != null) && (idx > 0)) {
        previousRow = rows.item(idx-1)
        shiftRow(row, previousRow)
        //updateOrderIndex(tbody)
    }

    //row = getParentElement(node, "TR")
    //previousRow = row.previousSibling
    //if (previousRow){
    //    shiftRow(row, previousRow)
    //}
}

function shiftRow(bottom, top){
    bottom.parentNode.insertBefore(bottom, top )
}

function updateOrderIndex(tbody) {
    // Set the orderindex in input fields again.
    // Id prefixes is everything before _
    var xre = new RegExp(/^orderindex_/)
    for (var c = 0; (cell = tbody.getElementsByTagName('INPUT').item(c)); c++) {
        if (cell.getAttribute('id')) {
            if (xre.exec(cell.id)) {
                cell.value=c
            }
        }
    }
}

// People browser support
// function to open the popup window
function personbrowser_openBrowser(node)
{
    fieldId = node.parentNode.parentNode.id
    lname = document.getElementById('lastname_' + fieldId);
    if (lname != null) {
        lastname = lname.value
    } else {
        lastname = ''
    }
    window.open('personbrowser_popup?fieldId=' + fieldId + '&search_text=' + lastname,'personbrowser_popup','toolbar=no,location=no,status=no,menubar=no,scrollbars=yes,resizable=yes,width=500,height=550');                 
}

// function to return a reference from the popup window back into the widget
function authorbrowser_setReference(fieldId, uid, label, fname, lname)
{
    element=document.getElementById('uid_' + fieldId);
    // First of all, add new row
    // Continue...
    element.value=uid;
    label_element=document.getElementById('id_' + fieldId);
    label_element.firstChild.nodeValue = label;
    firstname = document.getElementById('firstname_' + fieldId);
    //if (firstname.value == '') {firstname.value=fname;}
    firstname.value=fname;
    lastname = document.getElementById('lastname_' + fieldId);
    //if (lastname.value == '') {lastname.value=lname;}
    lastname.value=lname;
}
