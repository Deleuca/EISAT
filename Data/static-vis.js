d3.json("graph.json").then(function (data) {
    const container = document.getElementById("chart");
    const width = container.clientWidth;
    const height = container.clientHeight;

    const color = d3.scaleOrdinal([
        "#fd7f6f", "#7eb0d5", "#b2e061", "#bd7ebe", "#ffb55a",
        "#ffee65", "#beb9db", "#fdcce5", "#8bd3c7", "#f2a2e8",
        "#ffcfa5", "#d9c9a5"
    ]);

    const svg = d3.create("svg")
        .attr("width", width)
        .attr("height", height)
        .attr("viewBox", [0, 0, width, height])
        .attr("style", "max-width: 100%; height: auto;");

    const groups = data.nodes.filter(d => d.group !== -2).reduce((acc, node) => {
        acc[node.group] = acc[node.group] || [];
        acc[node.group].push(node);
        return acc;
    }, {});

    const groupKeys = Object.keys(groups);
    const groupCount = groupKeys.length;

    const groupPositions = [];
    const centerX = width / 2;
    const centerY = height / 2;

    // Determine positions for groups
    if (groupCount === 1) {
        groupPositions.push({ x: centerX, y: centerY });
    } else {
        const angleStep = (2 * Math.PI) / Math.min(groupCount, 15);
        const radius = Math.min(width, height) / 3;
        for (let i = 0; i < Math.min(groupCount, 15); i++) {
            const angle = i * angleStep;
            groupPositions.push({
                x: centerX + radius * Math.cos(angle),
                y: centerY + radius * Math.sin(angle)
            });
        }
    }

    // Assign fixed positions for group nodes
    groupKeys.forEach((groupKey, index) => {
        const groupNodes = groups[groupKey];
        const groupCenter = groupPositions[index];

        const angleStep = (2 * Math.PI) / groupNodes.length;
        const nodeRadius = 50; // Distance from group center

        groupNodes.forEach((node, i) => {
            node.fx = groupCenter.x + nodeRadius * Math.cos(i * angleStep);
            node.fy = groupCenter.y + nodeRadius * Math.sin(i * angleStep);
        });
    });

    // Assign positions for non-group nodes (-2 group) using a force simulation
    const simulation = d3.forceSimulation(data.nodes)
        .force("link", d3.forceLink(data.links).id(d => d.id).distance(100))
        .force("charge", d3.forceManyBody().strength(-300))
        .force("center", d3.forceCenter(width / 2, height / 2))
        .force("collide", d3.forceCollide(30))
        .on("tick", () => {
            data.nodes.forEach(node => {
                if (node.group === -2) {
                    node.x = Math.max(15, Math.min(width - 15, node.x));
                    node.y = Math.max(15, Math.min(height - 15, node.y));
                }
            });
        })
        .stop();

    for (let i = 0; i < 300; ++i) simulation.tick(); // Run simulation

    // Draw edges
    const link = svg.append("g")
        .selectAll("path")
        .data(data.links)
        .join("path")
        .attr("fill", "none")
        .attr("stroke-width", 2)
        .attr("stroke", "#999")
        .attr("d", d => {
            const dx = d.target.x - d.source.x;
            const dy = d.target.y - d.source.y;
            return `M${d.source.x},${d.source.y} L${d.target.x},${d.target.y}`;
        });

    // Draw nodes
    const nodeGroup = svg.append("g")
        .selectAll("g")
        .data(data.nodes)
        .join("g");

    nodeGroup.append("circle")
        .attr("r", 15)
        .attr("fill", d => color(d.group))
        .attr("cursor", "pointer");

    nodeGroup.append("text")
        .attr("text-anchor", "middle")
        .attr("dy", "0.35em")
        .style("font-size", "12px")
        .style("user-select", "none")
        .style("fill", "black")
        .style("font-family", "Arial, sans-serif")
        .text(d => (d.literal < 0 ? "¬x" : "x") + Math.abs(d.literal));

    nodeGroup.attr("transform", d => `translate(${d.x},${d.y})`);

    document.getElementById("chart").appendChild(svg.node());
});