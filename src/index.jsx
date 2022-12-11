import React from "react";
import ReactDOM from "react-dom/client";
import FaceDetectPageStream from "./routes/face_detect_page_stream"
import FaceRegistrationPage from "./routes/face_registration_page"

import "bootstrap/dist/css/bootstrap.min.css";
import {
  createBrowserRouter,
  RouterProvider,
} from "react-router-dom";
import Root from "./routes/root";

const router = createBrowserRouter([
  {
    path: "/",
    element: <Root />,
    children: [
      {
        path: "app",
        element: <FaceDetectPageStream />,
      },
      {
        path: "register",
        element: <FaceRegistrationPage />,
      },
    ],
  },
]);

const root = ReactDOM.createRoot(document.getElementById("root"));
root.render(
  <React.StrictMode>
    {/* <App /> */}
    <RouterProvider router={router} />
  </React.StrictMode>
);
