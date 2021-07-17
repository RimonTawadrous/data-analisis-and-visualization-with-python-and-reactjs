import React ,  { useState }  from "react";
import {Link} from "react-router-dom";
import "./NavBar.css"
const NavBar = () => {
    return (
           <div className = "navbar">
          <Link className="navbar__link" to="/annotators">Annotators</Link>
          <Link className="navbar__link" to="/annotations-dataset">Annotations & Dataset</Link>
      </div>   
    )
}

export default NavBar
