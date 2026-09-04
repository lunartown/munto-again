"use client";

import { useState } from "react";
import "./somoim.css";
import { GATHERINGS, byId } from "./data";
import { DetailScreen, ListScreen, PostScreen, ReportScreen, ReviewListScreen } from "./screens";

type Route =
  | { name: "list" }
  | { name: "detail"; id: string }
  | { name: "reviews"; id: string }
  | { name: "post"; id: string }
  | { name: "report"; id: string };

export default function SomoimPrototype() {
  const [stack, setStack] = useState<Route[]>([{ name: "list" }]);
  const route = stack[stack.length - 1];

  const push = (r: Route) => setStack((s) => [...s, r]);
  const pop = () => setStack((s) => (s.length > 1 ? s.slice(0, -1) : s));

  const gathering = "id" in route ? byId(route.id) : undefined;

  return (
    <div className="sm-root">
      <div className="sm-stage">
        <div className="sm-device">
          {route.name === "list" && (
            <ListScreen gatherings={GATHERINGS} onSelect={(id) => push({ name: "detail", id })} />
          )}
          {route.name === "detail" && gathering && (
            <DetailScreen
              gathering={gathering}
              onBack={pop}
              onOpenReviews={() => push({ name: "reviews", id: gathering.id })}
            />
          )}
          {route.name === "reviews" && gathering && (
            <ReviewListScreen
              gathering={gathering}
              onBack={pop}
              onOpenPost={() => push({ name: "post", id: gathering.id })}
              onReport={() => push({ name: "report", id: gathering.id })}
            />
          )}
          {route.name === "post" && gathering && <PostScreen gathering={gathering} onBack={pop} />}
          {route.name === "report" && gathering && (
            <ReportScreen gathering={gathering} onBack={pop} onDone={pop} />
          )}
        </div>
      </div>
    </div>
  );
}
