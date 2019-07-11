import React from 'react';
import { Modal, Button, Header } from 'semantic-ui-react';


class HelpModal extends React.Component {

  constructor(props) {
    super(props);
    this.state = {};
  }

  render() {
    return (
      <Modal floated="right" trigger={<Button>FAQ</Button>}>
        <Modal.Header>Relational Extraction FAQ</Modal.Header>
        <Modal.Content>

          <Header>What constitutes a Named Entity?</Header>
          <p>
            Entities can be generalized to proper nouns, and which fit into categories such as `individuals`, `places` etc.<br/>
            For example: <b>Michael Jordan of the Chicago Bulls is getting a 10-hour Netflix documentary in 2019</b> contains:<br/>
            <b>Michael Jordan</b> (Individual)<br/>
            <b>Chicago Bulls</b> (Organization)<br/>
            <b>Netflix</b> (Company)<br/>
          </p>

          <Header>What represents a Relation?</Header>
          <p>
            With regards to the task of <b>Open Relational Extraction</b>, we are interested only in the extraction of explicit relations that appear as words within a sentence.<br/>
            For example, the sentence: <b> When asked about the death of his brother, Buck, the only information Mackey could give the pastor was that of his participation in the Endian War of 2050.</b>:<br/>
            Mackey --- brother --- Buck <br/>
            Buck --- participation --- Endian War<br/>
            Endian War --- of --- 2050<br/>
            We extract only arguments for (Entity --- Relation --- Entity) that appear as is in the sentence.<br/>
            Higher level inferred semantic relations such as (Buck --- death --- Endian War) are also to be omitted.
          </p>

          <Header></Header>
          <p>
          </p>

        </Modal.Content>
      </Modal>
    )
  }
}

export default HelpModal;

