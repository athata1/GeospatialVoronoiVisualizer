import React, { useState, useContext } from "react";

const GraphContext = React.createContext();

export function useGraph() {
  return useContext(GraphContext);
}

export function GraphProvider({children}) {

    const [search, setSearch] = useState('')
    const [data, setData] = useState(null)

    const value = {
        search,
        setSearch,
        data,
        setData
    }

    return (
        <GraphContext.Provider value={value}>
            {children}
        </GraphContext.Provider>
    );
}
