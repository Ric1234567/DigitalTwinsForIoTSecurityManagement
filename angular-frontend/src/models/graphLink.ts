type lineStyle = {
    color: string,
    width: number
    type: string
}

export default class GraphLink {
    source: string
    target: string
    lineStyle: lineStyle = { color: "#000", width: 1, type: "solid" }

    constructor(source: string, target: string) {
        this.source = source
        this.target = target
    }

    setColor(color: string) {
        this.lineStyle.color = color
    }

    setWidth(width: number) {
        this.lineStyle.width = width
    }

    setLineType(type: string) {
        this.lineStyle.type = type
    }
}