import React from "react";
import ReactJson from "react-json-view";
import { useSnapshot } from "valtio";
import {subscriptions} from "./data";

import { removeFromList } from "../utils";

const JsonEdit = () => {
  const subsReadOnly = useSnapshot(subscriptions);

  return (
    <div>
      <ReactJson
        theme="ocean"
        src={subsReadOnly}
        displayDataTypes={false}
        onDelete={(del) => {
          removeFromList(
            subscriptions[del["namespace"][0]],
            del.existing_value
          );
        }}
        onAdd={() => {}}
        onEdit={(edit) => {
          console.log(edit);
          if (typeof edit.new_value !== String) {
            return false;
          }
          if (
            edit.existing_value &&
            edit.new_value &&
            edit.existing_value !== edit.new_value
          ) {
            removeFromList(
              subscriptions[edit["namespace"][0]],
              edit.existing_value
            );
            subscriptions[edit["namespace"][0]].push(edit.new_value);
            return true;
          } else if (
            edit.existing_value === null &&
            edit.new_value &&
            edit.new_value !== "null" &&
            !subscriptions[edit["namespace"][0]].includes(edit.new_value)
          ) {
            subscriptions[edit["namespace"][0]].push(edit.new_value);
            return true;
          }

          return false;
        }}
      />
    </div>
  );
};

export default JsonEdit;
