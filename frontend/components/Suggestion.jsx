import React from "react";

const Suggestion = ({ data }) => {
  return (
    <div>
      {data && "suggestion" in data ? (
        <h3 className="text-md text-black dark:text-white antialiased sm:subpixel-antialiased">
          {`Do you mean: `}
          <span>
            <a
              href={`search?search=${data.suggestion}`}
              alt="search"
              className="hover:underline text-blue-400 hover:text-blue-500"
            >
              {data.suggestion}
            </a>
          </span>
        </h3>
      ) : (
        <span />
      )}
    </div>
  );
};

export default Suggestion;
