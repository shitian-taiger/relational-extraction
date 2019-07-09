import _ from 'lodash';
import React from 'react';
import { Input, Button, Table } from 'semantic-ui-react';
import { ResultLine } from './ResultLine';
import equal from 'fast-deep-equal';

let initialState = {
  oieResults: [],
  dpResults: [],
  nerOieResults: [],
  oieResLines : [],
  dPLines: [],
  oieNerResLines: [],
  // Bitwise validity for user input
  validity: {oie: [], dp: [], nerOie: []},
  userInstances: [],
  sentence: ""
};

class Results extends React.Component {
  constructor(props) {
    super(props);
    this.state = initialState;
    this.state.sentence = props.sentence;
  }

  // Updating of Prediction Results: Set result array and instantiate validity index
  // Also updates sentence
  componentDidUpdate(prevProps, prevState, snapshot) {
    // Required since setState results in inf loop within componentDidUpdate
    if (!equal(this.props.results, prevProps.results)) {
      this.updatePredictionResults();
    }
  }
  updatePredictionResults() {
    let results = this.props.results;
    if (_.isEmpty(results)) {
      this.setState(initialState);
    } else {
      this.setState({
        oieResults: results.oie_prediction,
        dpResults: results.dp_prediction,
        nerOieResults: results.ner_oie_prediction,
        validity: {
          oie: results.oie_prediction.map(x => 0),
          dp: results.dp_prediction.map(x => 0),
          nerOie: results.ner_oie_prediction.map(x => 0)
        },
        sentence:this.props.sentence,
        userInstances: [],
        userLines: []
      });
      // We pass in results for updateInstances since state change for setState above doesn't
      // kick in until end of function call
      this.updateInstances(
        results.oie_prediction,
        results.dp_prediction,
        results.ner_oie_prediction,
      );
    }
  }

  updateInstances(oie, dp, ner_oie) {
    this.setState({
      oieResLines : this.getResArray("OIE", oie),
      dPLines: this.getResArray("DP", dp),
      oieNerResLines: this.getResArray("NER-OIE", ner_oie),
    });
  }
  // Process each prediction type (Array of tuples) into ResultLine(TableRow)
  getResArray(predictionType, arr) {
    let resLines = [];
    for (let i = 0; i < arr.length; i++) {
      let validity = false;
      if (predictionType === "USER") {
        validity = true;
      } else {
        let validityArr = this.getValidityArr(predictionType);
        validity = (validityArr[i] === 1) ? true : false;
      }
      let line = arr[i];
      resLines.push(<ResultLine
                    pType={predictionType}
                    key={i} // Each child in list requires unique key, not accessible in props
                    index={i}
                    text={line}
                    validity={validity}
                    validateInstance={this.instanceValidation}/>);
    }
    return resLines;
  }

  // Helpers for getting corresponding arrays for prediction types
  getValidityArr(pType) {
    if (pType === "OIE") {
      return this.state.validity.oie;
    } else if (pType === "DP") {
      return this.state.validity.dp;
    } else if (pType === "NER-OIE") {
      return this.state.validity.nerOie;
    } else {
      throw(new Error("Trying to get wrong result array type"));
    }
  }
  getResultArr(pType) {
    if (pType === "OIE") {
      return this.state.oieResults;
    } else if (pType === "DP") {
      return this.state.dpResults;
    } else if (pType === "NER-OIE") {
      return this.state.nerOieResults;
    } else {
      throw(new Error("Trying to get wrong result array type"));
    }
  }
  // Test for equality of instances for setting of validity of duplicates
  instancesEqual(instance1, instance2) {
    if (instance1[0].valueOf() === instance2[0].valueOf() &&
        instance1[0].valueOf() === instance2[0].valueOf() &&
        instance1[0].valueOf() === instance2[0].valueOf()) {
    }
  }
  setValidityDuplicate(result) {
    let result_instance = this.getResultArr(result.pType)[result.index];
    for (let idx in this.state.oieResults) {
      let instance = this.state.oieResults[idx];
      if (equal(instance, result_instance)) {
        this.getValidityArr("OIE")[idx] = this.getValidityArr(result.pType)[result.index];
      }
    }
    for (let idx in this.state.dpResults) {
      let instance = this.state.dpResults[idx];
      if (equal(instance, result_instance)) {
        this.getValidityArr("DP")[idx] = this.getValidityArr(result.pType)[result.index];
      }
    }
    for (let idx in this.state.nerOieResults) {
      let instance = this.state.nerOieResults[idx];
      if (equal(instance, result_instance)) {
        this.getValidityArr("NER-OIE")[idx] = this.getValidityArr(result.pType)[result.index];
      }
    }
    this.updateInstances(this.state.oieResults, this.state.dpResults, this.state.nerOieResults);
  }

  /** To be called by ResultLine child class, result should contain:
      pType : Prediction Type
      index : Index of instance within prediction type
      validity : Whether instance is valid
     */
  instanceValidation = (result) => {
    if (result.pType === "OIE" || result.pType === "DP" || result.pType === "NER-OIE") {
      let validityArr = this.getValidityArr(result.pType);
      validityArr[result.index] = (result.validity) ? 1 : 0;
      this.setValidityDuplicate(result);
    } else if (result.pType === "USER") {
      this.state.userInstances.splice(result.index, 1);
      this.setState({
        userInstances: this.state.userInstances,
        userLines: this.getResArray("USER", this.state.userInstances)
      });
    } else {
      console.log("Setting validity of invalid prediction type");
      throw(new Error("Invalid"));
    }
  }

  // Pass validations to parent Base
  confirmValidations() {
    if (this.state.oieResults.length === 0 &&
        this.state.nerOieResults.length === 0 &&
        this.state.dpResults.length === 0 &&
        this.state.userInstances.length === 0) {
      alert("No instances");
      }
    this.props.onValidated(this.state.validity, this.state.userInstances);
  }

  // InstanceCreator Helper
  addInstance = (instance) => {
    let newInstances = this.state.userInstances.concat([[instance.arg1Input, instance.relInput, instance.arg2Input]]);
    this.setState({
      userInstances: newInstances,
      userLines: this.getResArray("USER", newInstances),
    });
  }

  render() {
    return (
      <div className="Results">
        <div className="Results-Subheader"> OIE Results </div>
        <Table selectable className="Results-Table">
          <Table.Body>{this.state.oieResLines}</Table.Body>
        </Table>

        <div className="Results-Subheader"> NER-OIE Results </div>
        <Table selectable className="Results-Table">
          <Table.Body>{this.state.oieNerResLines}</Table.Body>
        </Table>

        <div className="Results-Subheader"> DP Results </div>
        <Table selectable className="Results-Table">
          <Table.Body>{this.state.dPLines}</Table.Body>
        </Table>

        <div className="Results-Subheader"> Custom Instances </div>
        <Table selectable className="Results-Table">
          <Table.Body>{this.state.userLines}</Table.Body>
        </Table>

        <InstanceCreator
          sentence={this.state.sentence}
          instanceCreate={this.addInstance}/>

        <Button style={{margin: "15px"}} onClick={() => this.confirmValidations()}>
          Confirm Instances
        </Button>
      </div>

    );
  }
}

class InstanceCreator extends React.Component {
  constructor(props) {
    super(props);
    this.state = {
      arg1Input: "",
      relInput: "",
      arg2Input: "",
      sentence: props.sentence
    };
    this.handleArg1Change = this.handleArg1Change.bind(this);
    this.handleRelChange = this.handleRelChange.bind(this);
    this.handleArg2Change = this.handleArg2Change.bind(this);
  }

  componentDidUpdate(prevProps, prevState, snapshot) {
    // Required since setState results in inf loop within componentDidUpdate
    if (!equal(this.props.sentence, prevProps.sentence)) {
      this.setState({
        sentence: this.props.sentence
      });
    }
  }

  handleArg1Change(event) {
    this.setState({arg1Input: event.target.value});
  }
  handleRelChange(event) {
    this.setState({relInput: event.target.value});
  }
  handleArg2Change(event) {
    this.setState({arg2Input: event.target.value});
  }

  addInstance() {
    if (this.state.sentence === "") {
      this.setState({errorMessage: "Predict on valid sentence first"});
    } else if (!this.state.arg1Input || !this.state.relInput || !this.state.arg2Input) {
      this.setState({errorMessage: "Ensure all fields are filled in"});
    } else if (!this.state.sentence.includes(this.state.arg1Input) ||
               !this.state.sentence.includes(this.state.relInput) ||
               !this.state.sentence.includes(this.state.arg2Input)) {
      this.setState({errorMessage: "Ensure arguments are contained within sentence"});
    } else {
      this.props.instanceCreate(this.state);
      this.setState({
        arg1Input: "",
        relInput: "",
        arg2Input: "",
      });
    }
  }

  // Allow `Enter` keypress to simulate button clicking
  handleKeyPress = (target) => {
    if(target.charCode === 13) { // `Enter` keycode
      this.addInstance()
    }
  }

  render() {
    return (
        <div>
          <Input className="InstanceCreator-Input"
                 placeholder="Entity One"
                 value={this.state.arg1Input}
                 onChange={this.handleArg1Change} />
          <Input className="InstanceCreator-Input"
                 placeholder="Relation"
                 value={this.state.relInput}
                 onChange={this.handleRelChange} />
          <Input className="InstanceCreator-Input"
                 placeholder="Entity Two"
                 value={this.state.arg2Input}
                 onChange={this.handleArg2Change}
                 onKeyPress={this.handleKeyPress}/>
          <Button onClick={() => this.addInstance()}>
            Add Relation
          </Button>
          <div style={{color: "Red"}}>{this.state.errorMessage}</div>
        </div>
    );
  }
}

export default Results;
