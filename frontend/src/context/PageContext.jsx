import { createContext, useContext, useState } from "react";

const ToggleContext = createContext();

export function ToggleProvider({ children }) {
  const [value, setValue] = useState(false);

  const toggle = () => setValue(true);

  return (
    <ToggleContext.Provider value={{ value, setValue, toggle }}>
      {children}
    </ToggleContext.Provider>
  );
}

export function useToggle() {
  return useContext(ToggleContext);
}