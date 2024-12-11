d3.json("graph.json").then(function (data) {
    const container = document.getElementById("chart");
    const width = container.clientWidth;
    const height = container.clientHeight;

    const color = d3.scaleOrdinal([
        "#fd7f6f", "#7eb0d5", "#b2e061", "#bd7ebe", "#ffb55a",
        "#ffee65", "#beb9db", "#fdcce5", "#8bd3c7"
    ]);

    const svg = d3.create("svg")
        .attr("width", width)
        .attr("height", height)
        .attr("viewBox", [0, 0, width, height])
        .attr("style", "max-width: 100%; height: auto;");

    // Force simulation for a standard spring layout
    const simulation = d3.forceSimulation(data.nodes)
        .force("link", d3.forceLink(data.links).id(d => d.id).distance(100))
        .force("charge", d3.forceManyBody().strength(-300))
        .force("center", d3.forceCenter(width / 2, height / 2))
        .force("collide", d3.forceCollide(30))
        .on("tick", ticked);

    // Helper function to check edge overlap
    function doesOverlap(d) {
        // Define simple heuristic to determine if an edge overlaps significantly
        const dx = d.target.x - d.source.x;
        const dy = d.target.y - d.source.y;
        return Math.abs(dx) < 30 && Math.abs(dy) < 30; // Adjust threshold as needed
    }

    // Draw edges
    const link = svg.append("g")
        .selectAll("path")
        .data(data.links)
        .join("path")
        .attr("fill", "none")
        .attr("stroke-width", d => 2.6 * Math.sqrt(d.value))
        .attr("stroke", "#999")
        .attr("d", d => doesOverlap(d) ? edgePath(d) : straightPath(d));

    // Function to generate B-spline paths
    function edgePath(d) {
        const dx = d.target.x - d.source.x;
        const dy = d.target.y - d.source.y;
        const dr = Math.sqrt(dx * dx + dy * dy); // Distance for curve
        return `M${d.source.x},${d.source.y} C${d.source.x + dr},${d.source.y}
                ${d.target.x - dr},${d.target.y} ${d.target.x},${d.target.y}`;
    }

    // Function for straight paths
    function straightPath(d) {
        return `M${d.source.x},${d.source.y} L${d.target.x},${d.target.y}`;
    }

    // Draw nodes
    const nodeGroup = svg.append("g")
        .selectAll("g")
        .data(data.nodes)
        .join("g");

    nodeGroup.append("circle")
        .attr("r", 18)
        .attr("fill", d => color(d.group))
        .attr("cursor", "pointer");

    nodeGroup.append("text")
        .attr("text-anchor", "middle")
        .attr("dy", "0.35em")
        .style("font-size", "15px")
        .style("user-select", "none")
        .style("fill", "black")
        .style("font-family", "'CMU Serif', serif")
        .text(d => (d.literal < 0 ? "¬x" : "x") + Math.abs(d.literal));

    function ticked() {
        link.attr("d", d => doesOverlap(d) ? edgePath(d) : straightPath(d));

        nodeGroup.attr("transform", d => `translate(${d.x},${d.y})`);
    }

    document.getElementById("chart").appendChild(svg.node());
});
