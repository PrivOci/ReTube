import { proxy } from "valtio";

export const subscriptions = proxy(
  JSON.parse(localStorage.getItem("subscriptions")) ?? {
    youtube: [],
    lbry: [],
    bitchute: [],
  }
);

export const config = proxy(
  JSON.parse(localStorage.getItem("config")) ?? {
    spell_checker: false,
  }
);