import {useContext} from "react";
import { ThemeContext } from "./ThemeContext";
import styles from "./Themetogglebutton.module.css";

export default function Themetogglebutton() {
    const {theme, toggleTheme} = useContext(ThemeContext);

    return(
        <label className={styles.switch}>
            <input
            type="checkbox" 
        onChange={toggleTheme} 
        checked={theme === "dark"} 
      />
      <span className={styles.slider}>
        <span className={styles.icon}>{theme === "dark" ? "🌙" : "☀️"}</span>
      </span>
        </label>
    )
}