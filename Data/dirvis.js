d3.json("graph.json").then(function (data) {
    const container = document.getElementById("chart");
    const width = container.clientWidth;
    const height = container.clientHeight;

    const color = d3.scaleOrdinal([
        "#fd7f6f", "#7eb0d5", "#b2e061", "#bd7ebe", "#ffb55a",
        "#ffee65", "#beb9db", "#fdcce5", "#8bd3c7"
    ]);

    // Track selected nodes
    const selectedNodes = new Set();
    const groupForceStrength = 0.1; // Adjust strength as needed
    const clusterForce = alpha => {
        for (const node of data.nodes) {
            const group = node.group;
            const clusterCenter = groupCenters[group] || { x: width / 2, y: height / 2 }; // Fallback to center
            // Move node slightly toward its cluster center
            node.vx -= (node.x - clusterCenter.x) * groupForceStrength * alpha;
            node.vy -= (node.y - clusterCenter.y) * groupForceStrength * alpha;
        }
    };

    const groupCenters = {
        0: { x: width * 0.2, y: height * 0.3 },
        1: { x: width * 0.3, y: height * 0.5 },
        2: { x: width * 0.7, y: height * 0.3 },
        3: { x: width * 0.5, y: height * 0.7 },
        4: { x: width * 0.8, y: height * 0.5 },
        "-2": { x: width * 0.5, y: height * 0.9 },
    };
    // Create a simulation with several forces.
    const simulation = d3.forceSimulation(data.nodes)
        .force("link", d3.forceLink(data.links).id(d => d.id).distance(200))
        .force("charge", d3.forceManyBody().strength(-30))
        .force("center", d3.forceCenter(width / 2, height / 2))
        .force("cluster", alpha => clusterForce(alpha))
        .on("tick", ticked);

    const svg = d3.create("svg")
        .attr("width", width)
        .attr("height", height)
        .attr("viewBox", [0, 0, width, height])
        .attr("style", "max-width: 100%; height: auto;");

    svg.append("defs").selectAll("marker")
    .data(["arrow"])
    .enter().append("marker")
    .attr("id", d => d)
    .attr("viewBox", "0 -5 10 10")
    .attr("refX", 15) // Adjust for arrow positioning
    .attr("refY", 0)
    .attr("markerWidth", 6)
    .attr("markerHeight", 6)
    .attr("orient", "auto")
    .append("path")
    .attr("d", "M0,-5L10,0L0,5")
    .attr("fill", "#999");


    const link = svg.append("g")
        .attr("stroke", "#999")
        .attr("stroke-opacity", 0.6)
        .selectAll()
        .data(data.links)
        .join("line")
        .attr("stroke-width", d => Math.sqrt(d.value))
        .attr("marker-end", "url(#arrow)"); // Add arrowhead

    const nodeGroup = svg.append("g")
        .selectAll()
        .data(data.nodes)
        .join("g")
        .attr("class", "node")
        .attr("cursor", "pointer");

    nodeGroup.append("circle")
        .attr("r", 18)
        .attr("fill", d => color(d.group))
        .on("mouseover", highlightHoveredEdges)
        .on("mouseout", resetHoverEffect)
        .on("click", toggleSelection);

    nodeGroup.append("text")
        .attr("text-anchor", "middle")
        .attr("dy", "0.35em")
        .style("font-size", "15px")
        .style("user-select", "none")
        .style("fill", "black")
        .style("font-family", "'CMU Serif', serif")
        .each(function (d) {
            const textElement = d3.select(this);

            const literalValue = Math.abs(d.literal);
            const isNegative = d.literal < 0;

            textElement.text(isNegative ? '¬x' : 'x');
            textElement.append("tspan")
                .text(literalValue)
                .style("font-size", "10px")
                .attr("baseline-shift", "sub");
        })
        .on("mouseover", highlightHoveredEdges)
        .on("mouseout", resetHoverEffect)
        .on("click", toggleSelection);

    nodeGroup.call(d3.drag()
        .on("start", dragstarted)
        .on("drag", dragged)
        .on("end", dragended));

    function ticked() {
        link
            .attr("x1", d => d.source.x)
            .attr("y1", d => d.source.y)
            .attr("x2", d => d.target.x)
            .attr("y2", d => d.target.y);

        nodeGroup
            .attr("transform", d => `translate(${d.x},${d.y})`);
    }

    function highlightHoveredEdges(event, d) {
        link.attr("stroke", link => {
            if (selectedNodes.has(link.source.id) || selectedNodes.has(link.target.id)) {
                return "#ff0000"; // Keep selected edges red
            }
            return (link.source.id === d.id) ? "#ffb3b3" : "#999"; // Highlight outgoing edges
        }).attr("stroke-opacity", link => {
            if (selectedNodes.has(link.source.id) || selectedNodes.has(link.target.id)) {
                return 0.8; // Keep selected edges at higher opacity
            }
            return (link.source.id === d.id) ? 0.8 : 0.2; // Adjust opacity for hovered edges
        });
    }

    function resetHoverEffect() {
        link.attr("stroke", link => {
            return selectedNodes.has(link.source.id) || selectedNodes.has(link.target.id) ? "#ff0000" : "#999";
        }).attr("stroke-opacity", link => {
            return selectedNodes.has(link.source.id) || selectedNodes.has(link.target.id) ? 0.8 : 0.6;
        });
    }

    function toggleSelection(event, d) {
        if (selectedNodes.has(d.id)) {
            selectedNodes.delete(d.id); // Deselect the node
        } else {
            selectedNodes.add(d.id); // Select the node
        }
        resetHoverEffect(); // Recompute edge highlights
    }

    function dragstarted(event) {
        if (!event.active) simulation.alphaTarget(0.3).restart();
        event.subject.fx = event.subject.x;
        event.subject.fy = event.subject.y;
    }

    function dragged(event) {
        event.subject.fx = event.x;
        event.subject.fy = event.y;
    }

    function dragended(event) {
        if (!event.active) simulation.alphaTarget(0);
        event.subject.fx = null;
        event.subject.fy = null;
    }

    document.getElementById("chart").appendChild(svg.node());

    window.onbeforeunload = function () {
        simulation.stop();
    };
}).catch(function (error) {
    console.error("Error loading the data: ", error);
});
