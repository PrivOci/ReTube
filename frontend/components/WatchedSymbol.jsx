import React from "react";
import { FontAwesomeIcon } from "@fortawesome/react-fontawesome";
import { faCheckSquare } from "@fortawesome/free-solid-svg-icons";

const WatchedSymbol = ({ withDot }) => {
  return (
    <div className="whitespace-pre">
      {withDot ? " • " : <span />}
      <FontAwesomeIcon icon={faCheckSquare} title="watched" />
    </div>
  );
};

export default WatchedSymbol;
