# model.py

from typing import Optional

from pydantic import BaseModel, Field, HttpUrl, computed_field


class CandidateResult(BaseModel):
    candidate_id: int = Field(alias="CandidateID")
    candidate_name: str = Field(alias="CandidateName")

    age: int = Field(alias="AGE_YR", ge=18)
    gender: str = Field(alias="Gender")
    dob: Optional[int] = Field(alias="DOB")

    political_party_name: str = Field(alias="PoliticalPartyName")
    symbol_code: int = Field(alias="SYMBOLCODE")
    symbol_name: str = Field(alias="SymbolName")

    ctzdistrict_id: Optional[int] = Field(alias="CTZDIST__1", default=None)
    ctzdistrict_name: Optional[str] = Field(alias="CTZDIST__2", default=None)

    district: str = Field(alias="DistrictName")
    state: str = Field(alias="StateName")
    state_id: int = Field(alias="STATE_ID")

    constituency_id: int = Field(alias="SCConstID")
    constituency_name: str | int = Field(alias="ConstName")

    total_vote_received: int = Field(alias="TotalVoteReceived", ge=0)
    round_no: int = Field(alias="R")
    election_status: Optional[str] = Field(alias="E_STATUS")

    father_name: Optional[str] = Field(alias="FATHER_NAME")
    spouse_name: Optional[str] = Field(alias="SPOUCE_NAME")
    qualification: Optional[str] = Field(alias="QUALIFICATION")
    institution: Optional[str] = Field(alias="NAMEOFINST")
    experience: Optional[str] = Field(alias="EXPERIENCE")
    other_details: Optional[str] = Field(alias="OTHERDETAILS")
    address: Optional[str] = Field(alias="ADDRESS")

    model_config = dict(populate_by_name=True, extra="ignore")

    @computed_field
    @property
    def candidate_image(self) -> HttpUrl:
        return HttpUrl(f"https://result.election.gov.np/Images/Candidate/{self.candidate_id}.jpg")

    @computed_field
    @property
    def symbol_image(self) -> HttpUrl:
        return HttpUrl(f"https://www.chunab.org/party-symbols/symbol-{self.symbol_code}.png")


CandidateResult.model_rebuild()
