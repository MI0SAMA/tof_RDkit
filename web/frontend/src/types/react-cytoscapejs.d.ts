declare module 'react-cytoscapejs' {
  import { Component } from 'react'
  import cytoscape from 'cytoscape'

  interface CytoscapeComponentProps {
    elements: cytoscape.ElementDefinition[]
    stylesheet?: cytoscape.Stylesheet | cytoscape.Stylesheet[]
    layout?: cytoscape.LayoutOptions
    style?: React.CSSProperties
    className?: string
    cy?: (cy: cytoscape.Core) => void
    wheelSensitivity?: number
    autoungrabify?: boolean
    autounselectify?: boolean
    panningEnabled?: boolean
    userPanningEnabled?: boolean
    zoomingEnabled?: boolean
    userZoomingEnabled?: boolean
    boxSelectionEnabled?: boolean
    minZoom?: number
    maxZoom?: number
    [key: string]: unknown
  }

  export default class CytoscapeComponent extends Component<CytoscapeComponentProps> {
    static normalizeElements(elements: cytoscape.ElementDefinition[]): cytoscape.ElementDefinition[]
  }
}
