import networkx as nx
from IPython.display import display, HTML
def d3_graph(G):
    text_edges = ''
    edges = G.edges()
    length = len(edges)
    for index, edge in enumerate(edges):
        text = '{"source":"'+edge[0]+'","target":"'+edge[1]+'"}'
        if index == length-1:
            text_edges = text_edges + text
        else:
            text_edges = text_edges + text +','
    return text_edges

def make_html_graph(edges, width=400, height=300, filename="d3.html"):
    """Code : http://christophergandrud.github.io/d3Network/"""
    head = """
    <!DOCTYPE html>
    <meta charset="utf-8">
    <body> 
    <style>
    .link {
    stroke: #666;
    opacity: 0.6;
    stroke-width: 1.5px;
    }
    .node circle {
    stroke: #fff;
    opacity: 0.6;
    stroke-width: 1.5px;
    }
    text {
    font: 7px serif;
    opacity: 0.6;
    pointer-events: none;
    }
    </style>

    <script src=http://d3js.org/d3.v3.min.js></script>
    <!--<script src="./d3.js"></script>-->

    <script> 
     var links = [ 
    """
    tail_1 = """
    ] ; 
     var nodes = {}

    // Compute the distinct nodes from the links.
    links.forEach(function(link) {
    link.source = nodes[link.source] ||
    (nodes[link.source] = {name: link.source});
    link.target = nodes[link.target] ||
    (nodes[link.target] = {name: link.target});
    link.value = +link.value;
    });

    var width = """+str(width)+"""
    height = """+str(height)

    tail_2 = """
    ;

    var force = d3.layout.force()
    .nodes(d3.values(nodes))
    .links(links)
    .size([width, height])
    .linkDistance(50)
    .charge(-200)
    .on("tick", tick)
    .start();

    var svg = d3.select("body").append("svg")
    .attr("width", width)
    .attr("height", height);

    var link = svg.selectAll(".link")
    .data(force.links())
    .enter().append("line")
    .attr("class", "link");

    var node = svg.selectAll(".node")
    .data(force.nodes())
    .enter().append("g")
    .attr("class", "node")
    .on("mouseover", mouseover)
    .on("mouseout", mouseout)
    .on("click", click)
    .on("dblclick", dblclick)
    .call(force.drag);

    node.append("circle")
    .attr("r", 8)
    .style("fill", "#3182bd");

    node.append("text")
    .attr("x", 12)
    .attr("dy", ".35em")
    .style("fill", "#3182bd")
    .text(function(d) { return d.name; });

    function tick() {
    link
    .attr("x1", function(d) { return d.source.x; })
    .attr("y1", function(d) { return d.source.y; })
    .attr("x2", function(d) { return d.target.x; })
    .attr("y2", function(d) { return d.target.y; });

    node.attr("transform", function(d) { return "translate(" + d.x + "," + d.y + ")"; });
    }

    function mouseover() {
    d3.select(this).select("circle").transition()
    .duration(750)
    .attr("r", 16);
    }

    function mouseout() {
    d3.select(this).select("circle").transition()
    .duration(750)
    .attr("r", 8);
    }
    // action to take on mouse click
    function click() {
    d3.select(this).select("text").transition()
    .duration(750)
    .attr("x", 22)
    .style("stroke-width", ".5px")
    .style("opacity", 1)
    .style("fill", "#E34A33")
    .style("font", "17.5px serif");
    d3.select(this).select("circle").transition()
    .duration(750)
    .style("fill", "#E34A33")
    .attr("r", 16)
    }

    // action to take on mouse double click
    function dblclick() {
    d3.select(this).select("circle").transition()
    .duration(750)
    .attr("r", 6)
    .style("fill", "#E34A33");
    d3.select(this).select("text").transition()
    .duration(750)
    .attr("x", 12)
    .style("stroke", "none")
    .style("fill", "#E34A33")
    .style("stroke", "none")
    .style("opacity", 0.6)
    .style("font", "7px serif");
    }

    </script>
    </body>
    """
    try:
        with open(filename, "w") as f:
            f.write(head)
            f.write(edges)
            f.write(tail_1)
            f.write(tail_2)
        f.close()
        print 'Generated.'
    except:
        print 'Problem!'
        
        
if __name__ == "__main__":
  edges = d3_graph(G)
  make_html_graph(edges) # make_html_graph(edges, 1000, 500)

# In Ipython
# %%HTML
# <iframe src="d3.html" width=100% height=500 frameborder=0></iframe>