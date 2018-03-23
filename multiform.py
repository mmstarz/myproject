<form method='POST'>
    {{form1.as_p}}
    <button type="submit" name="btnform1">Save Changes</button>
    </form>
    <form method='POST'>
    {{form2.as_p}}
    <button type="submit" name="btnform2">Save Changes</button>
    </form>
CODE

if request.method=='POST' and 'btnform1' in request.POST:
    do something...
if request.method=='POST' and 'btnform2' in request.POST:
    do something...