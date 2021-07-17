import './App.css';
import AnnotationsPage from './Pages/AnnotationsPage/AnnotationsPage';
import AnnotatorsPage from './Pages/AnnotatorsPage/AnnotatorsPage';
import { BrowserRouter as Router, Route, Switch } from "react-router-dom";
import NavBar from './Components/NavBar/NavBar';

function App() {

  
  return (
    <div className="App">
      <Router>
      <NavBar></NavBar>
      <Switch>
        <Route path="/annotators">
        <AnnotatorsPage/> 
        </Route>
        <Route path="/annotations-dataset">
        <AnnotationsPage/>
        </Route>
        <Route path="/">
        <AnnotationsPage/>
        </Route>
      </Switch>
      </Router>

    </div>
  );
}

export default App;
