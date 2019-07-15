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
            <b>2019</b> (Date)<br/>
          </p>


          <Header>What represents a Relation?</Header>
        <div>
        <div> With regards to the task of <b>Open Relational Extraction</b>, we are interested only in the extraction of explicit relations that appear as consecutive words within a sentence. </div>
        <div>
      For example, the sentence: <b> When asked about the death of his brother, Buck, the only information Mackey could give the pastor was that of his participation in the Endian War of 2050.</b> gives:
        </div>
        <b>Mackey --- brother --- Buck</b><br/>
        <b>Buck --- participation --- Endian War</b><br/>
        <b>Endian War --- of --- 2050</b><br/>
        <div>
        We extract only arguments for (Entity --- Relation --- Entity) that appear as is in the sentence.<br/>
        Higher level inferred semantic relations such as (Buck --- death --- Endian War) are also to be omitted.
        </div>
        </div>

          <Header>Sample Cases</Header>
        <div> <i> ***Pointers are numerically labeled for easier reference*** </i> </div>
        <br/>
        <div>
        <div> <b>After serving as Attorney General, Gilchrist returned to private practice in Jersey City.</b></div>
        <div> Valid instances: <br/> <b>Gilchrist --- serving --- Attorney General</b> <br/> <b>Gilchrist --- private practice --- Jersey City</b></div>
        <div> <b>(0)</b> In most cases, relations are represented by common nouns, e.g. `private practice`, verbial predicates such as <i>summoned, joined, conquered</i> that represent actions should not be valid relations between entities, nevertheless concrete relations do exist where verbial predicates are concerned, as in `serving` here.</div>
        </div>
        <br/>
        <div>
        <div> <b>In the 1840s, Wesley moved to the Indiana Great Plains.</b> </div>
        <div> Valid instances: <br/><b>Wesley --- moved --- Indiana Great Plains</b></div>
        <div> <b>(1)</b> Even though the ommission of the predicate <i>`to`</i> here makes the relation seem ambiguous, we enforce the extraction of individual noun-phrase representations of relations.</div>
        </div>
        <br/>
        <div>
        <div> <b>Nolan, son of Boris, has a son named Chester.</b> </div>
        <div> Valid instances: <br/><b>Nolan --- son --- Boris</b> <br/><b>Chester --- son --- Nolan</b></div>
        <div> <b>(2)</b> The ambiguity here is an issue since the relations should be directional. Where applicable, the relation should always take on the form of <b>Entity1 is/has relation of/with Entity2</b>.</div>
        </div>
        <br/>
        <div>
        <div> <b>Following a blow to the head by Napoleon, Gandalf died of a concussion a month later in 592BC.</b> </div>
        <div> Valid instances: <br/><b>Gandalf --- died --- 592BC</b></div>
        <div> <b>(3)</b> While concussion might seem like a valid relation between Gandalf and 592BC, note that it only makes sense given the information that he died in `592BC`, hence we omit it here.</div>
        </div>
        <br/>
        <div>
        <div> <b>Tom, Brady\'s brother who was awarded the Nobel Prize in 2090, has given him a million dollar loan.</b> </div>
        <div> Valid instances: <br/><b>Tom --- brother --- Brady</b> <br/> <b>Tom --- awarded --- Nobel Prize</b> <br/> </div>
        <div> <b>(4)</b> For when possessives are involved, i.e. <i>`Brady's`</i>, we omit the apostrophe since we are only interested in the Named Entity itself. <b>(5)</b> Also note that something like <b>Tom --- Nobel Prize --- 2090</b> is still valid even if the relation is itself a Named-Entity. <b>(6)</b> Lastly, while `million dollar loan` might seem like a relation, note that loan represents more of a an action than a concrete relation, hence we omit it here.</div>
        </div>
        <br/>
        <div>
        <div> <b>Fibichová also sang works from the French, Italian, German, and Russian opera repertories during her career.</b></div>
        <div> Valid instances: <br/><b> NONE </b></div>
        <div> <b>(7)</b> `Russian opera repertories`, while seemingly a proper noun, cannot be considered a Named Entity, we also automatically disregard `French / Italian / German` - `opera repertories` since they are not within a contiguous block within the sentence.</div>
        </div>
        <br/>
        <div>
        <div> <b>Fitzgerald was elected to the Seventy-seventh Congress</b></div>
        <div> Valid instances: <br/><b>Fitzgerald --- elected --- Seventy-seventh Congress</b></div>
        <div> <b>(8)</b> While the relation <b>Fitzgerald --- elected --- Congress</b> is likewise valid, we favor the more descriptive Named Entity in cases like these.</div>
        </div>

          <Header>Misc.</Header>
        <div>
        <div>
        <b>Is an instance such as `Tom --- moved --- to Brandenbourg` valid if `Tom --- moved to --- Brandenbourg` is a relation?</b>
        </div>
        No. Please invalidate that predicted instance and add in the latter.
        </div>
        <br/>
        <div>
        <b>What to do for sentences with no relation</b><br/>
        Simply confirm the invalid instances
        </div>

        </Modal.Content>
      </Modal>
    )
  }
}

export default HelpModal;
