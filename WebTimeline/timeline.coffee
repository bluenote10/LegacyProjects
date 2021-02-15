
###
Helpers
###

randomInt = (lower, upper=0) -> # bounds are included
  start = Math.random()
  if not lower?
    [lower, upper] = [0, lower]
  if lower > upper
    [lower, upper] = [upper, lower]
  return Math.floor(start * (upper - lower + 1) + lower)

dateString2Date = (dateString) ->
    if dateString.length == 10
        year  = parseInt(dateString[0..3], 10)
        month = parseInt(dateString[5..6], 10) - 1
        day   = parseInt(dateString[8..9], 10)
        #year  = dateString[0..3]
        #month = dateString[5..6]
        #day   = dateString[8..9]
        #console.log year, month, day
        return new Date(year, month, day)

dateDuration = (ts, te) ->
    diff = te - ts
    y = 1000 * 60 * 60 * 24 * 365.25
    ny = Math.floor(diff / y)
    diff = diff - (ny * y)
    d = 1000 * 60 * 60 * 24
    nd = Math.floor(diff / d)
    return "#{ny} years, #{nd} days"

###
Prepare data
###

ajxObj = null
if window.XMLHttpRequest
    ajxObj = new XMLHttpRequest()
else
    ajxObj = new ActiveXObject("Microsoft.XMLHTTP")
ajxObj.open("GET", "data.xml", false)
ajxObj.send()

ifChildExists = (node, childName, func) ->
    # https://studio.tellme.com/dom/ref/objects/node.html
    matchingChildren = node.getElementsByTagName(childName)
    if matchingChildren.length > 0
        func(matchingChildren[0].childNodes[0].nodeValue)

myXml = ajxObj.responseXML

groups = {}
data = []

groups['default'] = {
    color1: "#AA0050"
    color2: "#EE0050"
}

if myXml == null
    console.log "Error: xml data is corrupted"
    data = []
else
    # parse groups
    xmlGroups = myXml.getElementsByTagName("group")
    console.log 'Visible groups in xml data: ', xmlGroups
    for group, i in xmlGroups
        try
            name   = group.getElementsByTagName("name")[0].childNodes[0].nodeValue
            color1 = group.getElementsByTagName("color1")[0].childNodes[0].nodeValue
            color2 = group.getElementsByTagName("color2")[0].childNodes[0].nodeValue
            groups[name] = {
                color1: color1
                color2: color2
            }
        catch error
            console.log "Error: xml 'group' entry cannot be parsed:", error
            print error
    console.log "final groups: ", groups

    # parse periodes
    xmlPeriods = myXml.getElementsByTagName("period")
    console.log 'Visible periods in xml data: ', xmlPeriods
    for period, i in xmlPeriods
        console.log period
        name = timeS = timeE = link = category = null
        ifChildExists(period, "name",      (val) -> name = val)
        ifChildExists(period, "timeS",     (val) -> timeS = dateString2Date(val))
        ifChildExists(period, "timeE",     (val) -> timeE = dateString2Date(val))
        ifChildExists(period, "link",      (val) -> link = val)
        ifChildExists(period, "category",  (val) -> category = val)
        if category of groups
            category = groups[category]
        else
            category = groups['default']
        data[i] = {
            id: i
            start: timeS.getTime()
            end: timeE.getTime()
            name: name
            link: link
            category: category
        }

###
data = ({
    id: i
    start: randomInt(0, 20)
    end: randomInt(80, 100)
    } for i in [1..10])
###

console.log data

###
Create and fill canvas
###

paperElement = document.getElementById("canvas_container")
paperJQuery = $("#canvas_container")
canvasW = paperJQuery.width() # paperJQuery.attr('width')
canvasH = paperJQuery.height() # paperJQuery.attr('height')
console.log "canvas jquery: ", paperJQuery
paper = new Raphael(paperElement, canvasW, canvasH)

rects = []

for obj, i in data
    console.log obj.id
    rects[i] = paper.rect(obj.start, 10*i + 1, obj.end - obj.start, 8)
    rects[i].attr({
            'stroke-width': 0.8
            objId: i
            fill: obj.category.color1
            stroke: "black"
            r: 4
        })

    rects[i].objId = i

    rects[i].mouseover( ->
        obj = data[this.objId]
        console.log obj

        $("#infodiv").empty()
        table = $('<table></table>').addClass('infotable')
        appendToTable = (field, val) ->
            row = $('<tr></tr>')
            row.append($('<td></td>').text(field))
            row.append($('<td></td>').append(val))
            console.log row
            table.append(row)

        appendToTable("Name:", obj.name)
        appendToTable("From:", (new Date(obj.start)).toDateString())
        appendToTable("To:", (new Date(obj.end)).toDateString())
        appendToTable("Duration:", dateDuration(obj.start, obj.end))
        appendToTable("Link:", '<a href="' + obj.link + '">' + obj.link + '</a>')
        $('#infodiv').append(table)

        this.animate({ fill: obj.category.color2 }, 10, 'super_elastic');
        )
    rects[i].mouseout( ->
        #$("#infodiv").html($("#infodiv").html() + "mouseout<br/>")
        #$("#infodiv").empty()
        obj = data[this.objId]
        this.animate({ fill: obj.category.color1 }, 10, 'super_elastic');
        )

# prepare axis
axisRect = paper.rect(-5, 10, canvasW+10, 32)
axisRect.attr({
    "fill": "white"
    "stroke": "#BBB"
    "stroke-width": 1
    "opacity": 0.85
    })
###
axisRect.glow({
    "color": "#000"
    "width": 3
    "opacity": 0.3
    })
###
axisRect.translate(0.5, 0.5);

axisLine = paper.path("M -5 21 L #{canvasW + 10} 21")
axisLine.attr({
    "stroke": "black"
    "stroke-width": 1
    })
axisLine.translate(0.5, 0.5);

###
Zooming stuff
###

axisTicks = []
updateAxis = (minY, maxY) ->
    for tickEl in axisTicks
        tickEl.tick.remove()
        tickEl.labl.remove()
    axisTicks = []

    diff = maxY - minY
    incr =  if diff < 50
                5
            else if diff < 100
                10
            else if diff < 200
                25
            else if diff < 500
                50
            else if diff < 1000
                100
            else if diff < 2000
                250
            else if diff < 5000
                500
            else
                1000

    x = Math.floor(minY/incr) * incr + incr
    while x < maxY
        mappedX = scaling[1]*(new Date(x, 0, 0)).getTime() + scaling[0]
        tick = paper.path("M #{mappedX} 17 L #{mappedX} 25")
        tick.translate(0.5, 0.5)
        labl = paper.text(mappedX, 32, "#{x}")
        axisTicks.push({
            tick: tick
            labl: labl
            })
        x = x + incr

updatePositions = ->

    visibleRangeL = (0       - scaling[0]) / scaling[1]
    visibleRangeR = (canvasW - scaling[0]) / scaling[1]
    visibleYearL = (new Date(visibleRangeL)).getFullYear()
    visibleYearR = (new Date(visibleRangeR)).getFullYear()
    console.log "Visbible Range: (#{visibleRangeL}, #{visibleRangeR}) = (#{visibleYearL}, #{visibleYearR})"
    updateAxis(visibleYearL, visibleYearR)

    for rect, i in rects
        #rects[i] = paper.rect(obj.start, 10*i + 1, obj.end - obj.start, 8)
        obj = data[i]
        newXL = obj.start*scaling[1] + scaling[0]
        newXR = obj.end*scaling[1] + scaling[0]
        newYU = (10*(i)   + 1)*scaling[3] + scaling[2]
        newYD = (10*(i+1) - 1)*scaling[3] + scaling[2]
        rect.attr(x: newXL)
        rect.attr(y: newYU)
        rect.attr(width: newXR-newXL)
        rect.attr(height: newYD-newYU)

scaling = [0, 1, 46, 1]; # offset 0, scaling 1

minData = null
maxData = null
for obj in data
    minData = obj.start if minData > obj.start or minData == null
    maxData = obj.end if obj.end > maxData or maxData == null

initViewL = 20
initViewR = canvasW - 20

console.log "data min = ", minData, initViewL
console.log "data max = ", maxData, initViewR, canvasW

scaling[1] = (initViewL - initViewR) / (minData - maxData)
scaling[0] = initViewL - scaling[1]*minData

updatePositions()

doZoom = (event, delta) ->

    # transform to client coords
    cx = event.clientX - paperElement.offsetLeft
    cy = event.clientY - paperElement.offsetTop
    console.log event
    console.log delta
    console.log cx, cy

    oldscalingX = scaling[1]
    oldscalingY = scaling[3]

    if event.wheelDelta > 0
        scaling[1] = scaling[1]*1.1
        scaling[3] = scaling[3]*1.0
    else
        scaling[1] = scaling[1]/1.1
        scaling[3] = scaling[3]/1.0

    # recalc offsets
    oldoffsetX = scaling[0]
    oldoffsetY = scaling[2]
    scaling[0] = cx - scaling[1]/oldscalingX*(cx - oldoffsetX) #(oldscalingX*cx + scaling[1]*scaling[0] + scaling[1]*cx) / oldscalingX
    scaling[2] = cy - scaling[3]/oldscalingY*(cy - oldoffsetY) #(oldscalingY*cy + scaling[3]*scaling[2] + scaling[3]*cy) / oldscalingY

    console.log scaling
    console.log((cx - oldoffsetX) / oldscalingX)
    console.log((cx - scaling[0]) / scaling[1])
    console.log((cy - oldoffsetY) / oldscalingY)
    console.log((cy - scaling[2]) / scaling[3])

    # transform coordinates to new viewbox coordinates
    updatePositions()

    event.preventDefault()




$("#canvas_container").bind('mousewheel', (event, delta) -> doZoom(event, delta))
#paperElement.addEventListener("click", (event) -> doZoom(transformEventCoords(event), 2) )
#paperElement.addEventListener("DOMMouseScroll", (event) -> doZoom(event, 2))



###
Dragging stuff
###

lastX = -1
lastY = -1
clicking = false;

$('#canvas_container').mousedown( (evt) ->
        clicking = true
        $('#canvas_container').css('cursor', 'move');
        evt.stopPropagation();
        evt.preventDefault();
    )

$(document).mouseup( (evt) ->
        clicking = false
        $('#canvas_container').css('cursor', 'default');
        evt.stopPropagation();
        evt.preventDefault();
        lastX = -1
        lastY = -1
    )

$('#canvas_container').mousemove( (evt) ->
        if clicking == true
            deltaX = evt.pageX - lastX
            deltaY = evt.pageY - lastY

            console.log evt.pageX, evt.pageY, deltaX, deltaY

            if lastX != -1
                scaling[0] = scaling[0] + deltaX
                scaling[2] = scaling[2] + deltaY

            lastX = evt.pageX;
            lastY = evt.pageY;
            updatePositions()
    )

#paper.drag(null, -> console.log "drag", null)
#$("#canvas_container").bind("drag" , (event) -> console.log event)




###
paper = new Raphael(document.getElementById('canvas_container'), 600, 400)

circ = paper.circle(100, 100, 10)
circ.attr({fill: '#100'})

# circ.node.click -> alert("yes")

circ.node.onmouseover = ->
    this.style.cursor = 'pointer'
    $("#infodiv").html($("#infodiv").html() + "mouseover<br/>")
    #$("#infodiv").html("test")

circ.node.onclick = ->
    circ.animate({opacity: 0}, 200)
###


###
gcd = (a,b) ->
    if (b==0) then a else gcd(b, a % b)

$("#button").click ->
    $("#c").html "test"
    alert("test")
    a = $("#a").val()
    b = $("#b").val()
    $("#c").html gcd(a,b)
###


###
// coordinates of the last drag position
var lastX = 0, lastY = 0;

// record the click event on the image for drag and drop
var clicking = false;

// set clicking to true to record start of drag and drop
// and update the last coordinates
$('#mapHolder').mousedown(function(e){
        clicking = true;
    	lastX = e.pageX;
    	lastY = e.pageY;
    	$('#mapHolder').css('cursor', 'move');
    	e.stopPropagation();
    	e.preventDefault();
});

// when the mouse button is released set clicking to false
// to stop drag and drop
$(document).mouseup(function(e){
    	clicking = false;
    	$('#mapHolder').css('cursor', 'default');
    	e.stopPropagation();
    	e.preventDefault();
});

$('#mapHolder').mousemove(function(e){
    	// when mouse if moved check if user is also holding a mouse button
    	if (clicking == false) return;

    	var currentMapPosX = 0, currentMapPosY = 0;

    	// get difference between current and previous mouse position
    	if ((mapImage.attr('x') <= 0) && (mapImage.attr('x') >= (mapWidth - mapImage.attr('width'))))
    	{
    		currentMapPosX = e.pageX - lastX;
    	}

    	if ((mapImage.attr('y') <= 0) && (mapImage.attr('y') >= (mapHeight - mapImage.attr('height'))))
    	{
    		currentMapPosY = e.pageY - lastY;
    	}

    	// move the image
    	mapImage.translate(currentMapPosX, currentMapPosY);

    	// record previous position
    	lastX = e.pageX;
    	lastY = e.pageY;

    	// check for image edge
    	adjustMapEdge();
});
###
