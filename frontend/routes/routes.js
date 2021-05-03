import { faFire, faNewspaper, faEdit, faUserCog } from "@fortawesome/free-solid-svg-icons";

const routes = [
  {
    name: "Popular",
    faIcon: faFire,
    path: "/popular",
  },
  {
    name: "Subscriptions",
    faIcon: faNewspaper,
    path: "/subscriptions",
  },
  {
    name: "Settings",
    faIcon: faUserCog,
    path: "/settings",
  },
  {
    name: "JSON View",
    faIcon: faEdit,
    path: "/json",
  },
];

export default routes;
