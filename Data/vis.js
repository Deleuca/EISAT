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

    const groupForceStrength = 0.025; // Smaller value for weaker attraction

    const clusterForce = alpha => {
        for (const node of data.nodes) {
            const group = node.group;
            const clusterCenter = groupCenters[group] || { x: width / 2, y: height / 2 };
            // Move node slightly toward its cluster center, but with less strength
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
            if (mstEdgesByNodeId[nodeId].has(eKey)) {
                return true;
            }
        }
        return false;
    }

    function toggleSelection(event, d) {
        if (selectedNodes.has(d.id)) {
            selectedNodes.delete(d.id);
        } else {
            selectedNodes.add(d.id);
        }
        updateVisuals();
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

    async function runMSTToggle(event, d) {
        event.preventDefault();

        if (mstEdgesByNodeId[d.id]) {
            delete mstEdgesByNodeId[d.id];
            updateVisuals();
        } else {
            const {componentNodes, componentEdges} = getConnectedComponent(d.id, data);
            const mstEdges = computeMST(componentNodes, componentEdges);
            mstEdgesByNodeId[d.id] = new Set();

            for (let i = 0; i < mstEdges.length; i++) {
                const e = mstEdges[i];
                const eK = edgeKey(e.source.id, e.target.id).toString();
                mstEdgesByNodeId[d.id].add(eK);
                updateVisuals();
                await new Promise(resolve => setTimeout(resolve, 300));
            }
        }
    }

    function getConnectedComponent(startId, data) {
        const adj = {};
        data.nodes.forEach(n => { adj[n.id] = []; });
        data.links.forEach(l => {
            adj[l.source.id].push(l.target.id);
            adj[l.target.id].push(l.source.id);
        });

        const visited = new Set();
        const queue = [startId];
        visited.add(startId);

        while (queue.length > 0) {
            const curr = queue.shift();
            for (const neigh of adj[curr]) {
                if (!visited.has(neigh)) {
                    visited.add(neigh);
                    queue.push(neigh);
                }
            }
        }

        const componentNodes = data.nodes.filter(n => visited.has(n.id));
        const componentNodeIds = new Set(componentNodes.map(n => n.id));
        const componentEdges = data.links.filter(l => componentNodeIds.has(l.source.id) && componentNodeIds.has(l.target.id));

        return {componentNodes, componentEdges};
    }

    function computeMST(nodes, links) {
        const sortedLinks = [...links].sort((a, b) => a.value - b.value);
        const uf = new UnionFind(nodes.map(n => n.id));

        const mst = [];
        for (const edge of sortedLinks) {
            if (uf.union(edge.source.id, edge.target.id)) {
                mst.push(edge);
            }
        }
        return mst;
    }

    class UnionFind {
        constructor(elements) {
            this.parent = {};
            this.rank = {};
            for (const e of elements) {
                this.parent[e] = e;
                this.rank[e] = 0;
            }
        }

        find(x) {
            if (this.parent[x] !== x) {
                this.parent[x] = this.find(this.parent[x]);
            }
            return this.parent[x];
        }

        union(a, b) {
            const rootA = this.find(a);
            const rootB = this.find(b);

            if (rootA === rootB) return false;
            if (this.rank[rootA] < this.rank[rootB]) {
                this.parent[rootA] = rootB;
            } else if (this.rank[rootB] < this.rank[rootA]) {
                this.parent[rootB] = rootA;
            } else {
                this.parent[rootB] = rootA;
                this.rank[rootA] += 1;
            }
            return true;
        }
    }

}).catch(function (error) {
    console.error("Error loading the data: ", error);
});

window.addEventListener('resize', function() {
  const container = document.getElementById("chart");
  const newWidth = container.clientWidth;
  const newHeight = container.clientHeight;

  svg
    .attr("width", newWidth)
    .attr("height", newHeight)
    .attr("viewBox", [0, 0, newWidth, newHeight]);

  // Update the force center if you're using one:
  simulation.force("center", d3.forceCenter(newWidth / 2, newHeight / 2));

  // If you want to smoothly reapply forces:
  simulation.alpha(0.3).restart();
});
