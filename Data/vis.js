d3.json("graph.json").then(function (data) {
    const container = document.getElementById("chart");
    const width = container.clientWidth;
    const height = container.clientHeight;

    const color = d3.scaleOrdinal([
        "#fd7f6f", "#7eb0d5", "#b2e061", "#bd7ebe", "#ffb55a",
        "#ffee65", "#beb9db", "#fdcce5", "#8bd3c7", "#f2a2e8",
        "#ffcfa5", "#d9c9a5"
    ]);

    const selectedNodes = new Set();
    const mstEdgesByNodeId = {};
    const blueEdgesSet = new Set(); // For blue edges from middle-click
    let hoveredNodeId = null;
    let pendingMiddleNode = null;

    function edgeKey(a, b) { return a < b ? [a, b] : [b, a]; }

    const attractionStrength = 0.05; // Attraction strength between nodes of the same group
    const repulsionStrength = 0.1;  // Repulsion strength between nodes of different groups

    const clusterForce = alpha => {
        for (const node of data.nodes) {
            // Apply attractive force for nodes in the same group
            for (const otherNode of data.nodes) {
                if (node !== otherNode) {
                    const dx = node.x - otherNode.x;
                    const dy = node.y - otherNode.y;
                    const distance = Math.sqrt(dx * dx + dy * dy);
                    const force = (node.group === otherNode.group)
                        ? -attractionStrength * alpha / Math.max(distance, 1)  // Attraction
                        : repulsionStrength * alpha / Math.max(distance, 1);  // Repulsion

                    node.vx -= force * dx;
                    node.vy -= force * dy;
                }
            }
        }
    };

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

    const link = svg.append("g")
        .selectAll()
        .data(data.links)
        .join("line")
        .attr("stroke-width", d => 2.6 * Math.sqrt(d.value));

    const nodeGroup = svg.append("g")
        .selectAll()
        .data(data.nodes)
        .join("g")
        .attr("class", "node")
        .attr("cursor", "pointer");

    nodeGroup.append("circle")
        .attr("r", 18)
        .attr("fill", d => color(d.group))
        .on("mouseover", hoveredNode)
        .on("mouseout", unhovered)
        .on("click", toggleSelection)
        .on("contextmenu", runMSTToggle)
        .on("auxclick", handleMiddleClick);

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
        .on("mouseover", hoveredNode)
        .on("mouseout", unhovered)
        .on("click", toggleSelection)
        .on("contextmenu", runMSTToggle)
        .on("auxclick", handleMiddleClick);

    nodeGroup.call(d3.drag()
        .on("start", dragstarted)
        .on("drag", dragged)
        .on("end", dragended));

    document.getElementById("chart").appendChild(svg.node());

    // Call updateVisuals once at the end to ensure edges are visible from the start
    updateVisuals();

    window.onbeforeunload = function () {
        simulation.stop();
    };

    function ticked() {
        link
            .attr("x1", d => d.source.x)
            .attr("y1", d => d.source.y)
            .attr("x2", d => d.target.x)
            .attr("y2", d => d.target.y);

        nodeGroup
            .attr("transform", d => `translate(${d.x},${d.y})`);
    }

    function handleMiddleClick(event, d) {
        if (event.button !== 1) return;
        event.preventDefault();

        if (!pendingMiddleNode) {
            pendingMiddleNode = d;
        } else {
            if (pendingMiddleNode.id !== d.id) {
                const eK = edgeKey(pendingMiddleNode.id, d.id).toString();
                const edgeExists = data.links.some(l =>
                    (l.source.id === pendingMiddleNode.id && l.target.id === d.id) ||
                    (l.source.id === d.id && l.target.id === pendingMiddleNode.id)
                );

                if (edgeExists) {
                    // Toggle the highlight
                    if (blueEdgesSet.has(eK)) {
                        // Edge already highlighted, unhighlight it
                        blueEdgesSet.delete(eK);
                    } else {
                        // Edge not highlighted, highlight it
                        blueEdgesSet.add(eK);
                    }
                    updateVisuals();
                }
            }
            pendingMiddleNode = null;
        }
    }

    function hoveredNode(event, d) {
        hoveredNodeId = d.id;
        updateVisuals();
    }

    function unhovered() {
        hoveredNodeId = null;
        updateVisuals();
    }

    function edgeBaseColor(l) {
        const eK = edgeKey(l.source.id, l.target.id).toString();
        if (isEdgeInAnyMST(eK)) return "#00ff00"; // MST
        if (blueEdgesSet.has(eK)) return "#ff9f49"; // Orange
        if (selectedNodes.has(l.source.id) || selectedNodes.has(l.target.id)) return "#ff0000"; // Selected
        return "#999"; // Normal
    }

    function updateVisuals() {
        const hoveredEdges = new Set();
        let hoveredLiteral = null;

        if (hoveredNodeId !== null) {
            const hoveredNode = data.nodes.find(n => n.id === hoveredNodeId);
            hoveredLiteral = hoveredNode ? hoveredNode.literal : null;

            data.links.forEach(l => {
                if (l.source.id === hoveredNodeId || l.target.id === hoveredNodeId) {
                    hoveredEdges.add(edgeKey(l.source.id, l.target.id).toString());
                }
            });
        }

        link
            .attr("stroke", l => edgeBaseColor(l))
            .attr("stroke-opacity", l => {
                const eK = edgeKey(l.source.id, l.target.id).toString();
                let baseOpacity = 0.6;
                const c = edgeBaseColor(l);
                if (c === "#00ff00" || c === "#ff9f49") baseOpacity = 0.9;
                else if (c === "#ff0000") baseOpacity = 0.8;

                if (hoveredNodeId === null) {
                    return baseOpacity;
                } else {
                    return hoveredEdges.has(eK) ? Math.min(baseOpacity + 0.2, 1) : 0.3;
                }
            });

        nodeGroup.select("circle")
            .attr("fill-opacity", d => {
                if (hoveredNodeId === null) return 1.0;
                if (d.id === hoveredNodeId || (hoveredLiteral !== null && d.literal === hoveredLiteral)) {
                    return 1.0;
                }
                return 0.3;
            });

        nodeGroup.select("text")
            .attr("fill-opacity", d => {
                if (hoveredNodeId === null) return 1.0;
                if (d.id === hoveredNodeId || (hoveredLiteral !== null && d.literal === hoveredLiteral)) {
                    return 1.0;
                }
                return 0.3;
            });
    }

    function isEdgeInAnyMST(eKey) {
        for (const nodeId in mstEdgesByNodeId) {
            if (mstEdgesByNodeId[nodeId].has(eKey)) return true;
        }
        return false;
    }

    function toggleSelection(event, d) {
        if (event.ctrlKey || event.shiftKey) {
            // CTRL or SHIFT clicked: multiple selection
            if (selectedNodes.has(d.id)) {
                selectedNodes.delete(d.id);
            } else {
                selectedNodes.add(d.id);
            }
        } else {
            // Normal click: clear selection
            selectedNodes.clear();
            selectedNodes.add(d.id);
        }
        updateVisuals();
    }

    function runMSTToggle(event, d) {
        if (event.button !== 2) return; // Right click

        // Toggle MST visibility for this node
        if (mstEdgesByNodeId[d.id]) {
            delete mstEdgesByNodeId[d.id];
        } else {
            mstEdgesByNodeId[d.id] = new Set();
        }

        updateVisuals();
    }

    function dragstarted(event, d) {
        if (!event.active) simulation.alphaTarget(0.3).restart();
        d.fx = d.x;
        d.fy = d.y;
    }

    function dragged(event, d) {
        d.fx = event.x;
        d.fy = event.y;
    }

    function dragended(event, d) {
        if (!event.active) simulation.alphaTarget(0);
        d.fx = null;
        d.fy = null;
    }
});
