type graphLabel = {
    show: boolean
}
type itemStyle = {
    color: string
}

export default class GraphNode {
    name: string
    label: graphLabel = { show: true }
    itemStyle: itemStyle = { color: "#000" }

    constructor(name: string, color: string) {
        this.name = name
        this.itemStyle.color = color
    }
}