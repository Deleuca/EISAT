// Fetch the JSON data
d3.json("graph.json").then(function(data) {
    // Specify the dimensions of the chart.
    const container = document.getElementById("chart");
    const width = container.clientWidth;
    const height = container.clientHeight;

    // Specify the color scale.
    const color = d3.scaleOrdinal([
        "#fd7f6f", "#7eb0d5", "#b2e061", "#bd7ebe", "#ffb55a",
        "#ffee65", "#beb9db", "#fdcce5", "#8bd3c7"
    ]);

    // Create a simulation with several forces.
    const simulation = d3.forceSimulation(data.nodes)
        .force("link", d3.forceLink(data.links).id(d => d.id).distance(200))
        .force("charge", d3.forceManyBody().strength(-30))
        .force("center", d3.forceCenter(width / 2, height / 2))
        .on("tick", ticked);

    // Create the SVG container.
    const svg = d3.create("svg")
        .attr("width", width)
        .attr("height", height)
        .attr("viewBox", [0, 0, width, height])
        .attr("style", "max-width: 100%; height: auto;");

    // Add a line for each link.
    const link = svg.append("g")
        .attr("stroke", "#999")
        .attr("stroke-opacity", 0.6)
        .selectAll()
        .data(data.links)
        .join("line")
        .attr("stroke-width", d => Math.sqrt(d.value));

    // Create the nodes and append to group
    const nodeGroup = svg.append("g")
        .selectAll()
        .data(data.nodes)
        .join("g")
        .attr("class", "node")
        .attr("cursor", "pointer"); // Add pointer cursor for better UX

    // Add a circle for each node
    nodeGroup.append("circle")
        .attr("r", 18) // Node size
        .attr("fill", d => color(d.group))
        .on("mouseover", highlightEdges) // Highlight edges on hover
        .on("mouseout", resetEdges); // Reset edges when mouse leaves

    // Create labels for the nodes
    nodeGroup.append("text")
        .attr("text-anchor", "middle") // Center the text horizontally
        .attr("dy", "0.35em") // Center the text vertically
        .style("font-size", "15px")
        .style("user-select", "none") // Prevent text from being highlightable
        .style("fill", "black")
        .style("font-family", "'CMU Serif', serif") // Use Computer Modern font
        .each(function(d) {
            const textElement = d3.select(this);

            const literalValue = Math.abs(d.literal); // Get the absolute value of literal
            const isNegative = d.literal < 0; // Check if the literal is negative

            // Start by adding 'x'
            textElement.text(isNegative ? '¬x' : 'x');

            // Add the literal value as a subscript
            textElement.append("tspan")
                .text(literalValue) // Add the numeric literal
                .style("font-size", "10px") // Make the subscript smaller
                .attr("baseline-shift", "sub"); // Shift the subscript downward
        });

    // Add a drag behavior to the node group (circle + label)
    nodeGroup.call(d3.drag()
        .on("start", dragstarted)
        .on("drag", dragged)
        .on("end", dragended));

    // Set the position attributes of links and nodes each time the simulation ticks.
    function ticked() {
        link
            .attr("x1", d => d.source.x)
            .attr("y1", d => d.source.y)
            .attr("x2", d => d.target.x)
            .attr("y2", d => d.target.y);

        nodeGroup
            .attr("transform", d => `translate(${d.x},${d.y})`); // Update both circle and text position
    }

    // Highlight edges when hovering over a node
    function highlightEdges(event, d) {
        link
            .attr("stroke", link => (link.source.id === d.id || link.target.id === d.id) ? "#ff0000" : "#999")
            .attr("stroke-opacity", link => (link.source.id === d.id || link.target.id === d.id) ? 0.8 : 0.2); // Adjust opacity
    }

    function resetEdges() {
        link
            .attr("stroke", "#999")
            .attr("stroke-opacity", 0.6);
    }

    // Add hover behavior to text elements
    nodeGroup.selectAll("text")
        .on("mouseover", highlightEdges)
        .on("mouseout", resetEdges);

    

    // Reheat the simulation when drag starts, and fix the subject position.
    function dragstarted(event) {
        if (!event.active) simulation.alphaTarget(0.3).restart();
        event.subject.fx = event.subject.x;
        event.subject.fy = event.subject.y;
    }

    // Update the subject (dragged node) position during drag.
    function dragged(event) {
        event.subject.fx = event.x;
        event.subject.fy = event.y;
    }

    // Restore the target alpha so the simulation cools after dragging ends.
    function dragended(event) {
        if (!event.active) simulation.alphaTarget(0);
        event.subject.fx = null;
        event.subject.fy = null;
    }

    // Add the SVG to the #chart div in the HTML.
    document.getElementById("chart").appendChild(svg.node());

    // Stop the simulation once the page is unloaded.
    window.onbeforeunload = function() {
        simulation.stop();
    };
}).catch(function(error) {
    console.error('Error loading the data: ', error);
});
